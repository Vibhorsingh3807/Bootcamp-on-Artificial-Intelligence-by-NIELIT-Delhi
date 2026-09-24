import numpy as np
from collections import deque
from sklearn.neighbors import KNeighborsClassifier

# All standard sign gestures recognized by EchoSign
GESTURE_LABELS = [
    "HELLO",
    "NAMASTE",
    "THANK YOU",
    "YES",
    "NO",
    "PLEASE",
    "WATER",
    "FOOD",
    "PAIN",
    "DOCTOR",
    "PEACE",
    "I LOVE YOU",
    "OK"
]

class SignRecognizer:
    def __init__(self, history_len=7):
        # Rolling queue to keep last 7 frame predictions
        # Matlab pichle 7 frames ka consensus lenge taaki thoda sa haath hilne par flicker na ho
        self.history = deque(maxlen=history_len)
        self.model = None
        self._build_and_train_model()

    def _normalize_landmarks(self, landmarks):
        pts = np.array(landmarks, dtype=float)
        if pts.shape != (21, 3):
            pts = pts.reshape((21, 3))
        
        # Point 0 is the wrist. Shift everything so wrist becomes (0, 0, 0)
        # Wrist ko origin banate hain taaki screen pe haath kahan hai usse fark na pade
        wrist = pts[0].copy()
        pts = pts - wrist
        
        # Point 9 is middle finger knuckle (MCP joint)
        # Palm length se divide kar rahe hain taaki agar camera se door ho ya paas, size scale same rahe
        palm_size = np.linalg.norm(pts[9])
        if palm_size > 1e-6:
            pts = pts / palm_size
        return pts

    def extract_features(self, landmarks):
        pts = self._normalize_landmarks(landmarks)
        flat_coords = pts.flatten()

        # Key finger distances (thumb to tips, index to middle, etc.)
        d_thumb_index = np.linalg.norm(pts[4] - pts[8])
        d_thumb_middle = np.linalg.norm(pts[4] - pts[12])
        d_thumb_pinky = np.linalg.norm(pts[4] - pts[20])
        d_index_middle = np.linalg.norm(pts[8] - pts[12])
        d_middle_ring = np.linalg.norm(pts[12] - pts[16])
        d_ring_pinky = np.linalg.norm(pts[16] - pts[20])

        # Distance of each fingertip from wrist
        # Har ungli ka tip wrist se kitna door hai (extended ya curled check karne ke liye)
        d_tip_wrist = [
            np.linalg.norm(pts[4]),
            np.linalg.norm(pts[8]),
            np.linalg.norm(pts[12]),
            np.linalg.norm(pts[16]),
            np.linalg.norm(pts[20])
        ]

        # Finger extension ratios (tip distance / knuckle distance)
        # Ratio 1.15 se bada hai matlab ungli khuli hui hai, chhota hai matlab band hai
        ext_ratios = [
            np.linalg.norm(pts[4]) / (np.linalg.norm(pts[2]) + 1e-6),
            np.linalg.norm(pts[8]) / (np.linalg.norm(pts[6]) + 1e-6),
            np.linalg.norm(pts[12]) / (np.linalg.norm(pts[10]) + 1e-6),
            np.linalg.norm(pts[16]) / (np.linalg.norm(pts[14]) + 1e-6),
            np.linalg.norm(pts[20]) / (np.linalg.norm(pts[18]) + 1e-6),
        ]

        # How clustered together all fingertips are (for Food pinch)
        tips = pts[[4, 8, 12, 16, 20]]
        tip_center = np.mean(tips, axis=0)
        cluster_dispersion = np.mean([np.linalg.norm(t - tip_center) for t in tips])

        additional = np.array([
            d_thumb_index, d_thumb_middle, d_thumb_pinky,
            d_index_middle, d_middle_ring, d_ring_pinky,
            *d_tip_wrist,
            *ext_ratios,
            cluster_dispersion
        ])

        return np.concatenate([flat_coords, additional])

    def _generate_synthetic_pose(self, gesture):
        # Base hand model with 21 coordinates
        # Reference template coordinates for training KNN
        pts = np.zeros((21, 3))
        pts[1] = [-0.3, -0.3, 0.0]  # thumb CMC
        pts[2] = [-0.5, -0.6, 0.0]  # thumb MCP
        pts[5] = [-0.3, -1.0, 0.0]  # index MCP
        pts[9] = [0.0, -1.1, 0.0]   # middle MCP
        pts[13] = [0.25, -1.0, 0.0] # ring MCP
        pts[17] = [0.45, -0.85, 0.0]# pinky MCP

        def set_finger(mcp_idx, extended, spread_x=0.0, curl_y=0.4):
            base = pts[mcp_idx]
            if extended:
                pts[mcp_idx + 1] = base + [spread_x * 0.3, -0.4, 0.0]
                pts[mcp_idx + 2] = base + [spread_x * 0.6, -0.7, 0.0]
                pts[mcp_idx + 3] = base + [spread_x * 0.9, -1.0, 0.0]
            else:
                pts[mcp_idx + 1] = base + [0.0, -0.15, 0.2]
                pts[mcp_idx + 2] = base + [0.0, -0.05, 0.35]
                pts[mcp_idx + 3] = base + [0.0, curl_y, 0.3]

        def set_thumb(extended, up=False):
            if up:
                pts[3] = [-0.5, -0.9, 0.0]
                pts[4] = [-0.5, -1.3, 0.0]
            elif extended:
                pts[3] = [-0.7, -0.8, 0.0]
                pts[4] = [-0.9, -1.0, 0.0]
            else:
                pts[3] = [-0.3, -0.6, 0.1]
                pts[4] = [-0.1, -0.6, 0.1]

        if gesture == "HELLO":
            set_thumb(extended=True)
            set_finger(5, extended=True, spread_x=-0.2)
            set_finger(9, extended=True, spread_x=0.0)
            set_finger(13, extended=True, spread_x=0.15)
            set_finger(17, extended=True, spread_x=0.3)
        elif gesture == "NAMASTE":
            # Both hands together upright; single hand template has all fingers closed flat upright
            set_thumb(extended=False)
            set_finger(5, extended=True, spread_x=0.0)
            set_finger(9, extended=True, spread_x=0.0)
            set_finger(13, extended=True, spread_x=0.0)
            set_finger(17, extended=True, spread_x=0.0)
            pts[4] = [-0.1, -0.8, 0.0]
        elif gesture == "THANK YOU":
            set_thumb(extended=False)
            set_finger(5, extended=True, spread_x=-0.05)
            set_finger(9, extended=True, spread_x=0.0)
            set_finger(13, extended=True, spread_x=0.05)
            set_finger(17, extended=True, spread_x=0.1)
        elif gesture == "YES":
            set_thumb(extended=True, up=True)
            set_finger(5, extended=False)
            set_finger(9, extended=False)
            set_finger(13, extended=False)
            set_finger(17, extended=False)
        elif gesture == "NO":
            set_thumb(extended=False)
            base_idx = pts[5]
            pts[6] = base_idx + [0.1, -0.4, 0.0]
            pts[7] = base_idx + [0.12, -0.7, 0.0]
            pts[8] = base_idx + [0.14, -1.0, 0.0]
            base_mid = pts[9]
            pts[10] = base_mid + [-0.05, -0.4, 0.0]
            pts[11] = base_mid + [-0.07, -0.7, 0.0]
            pts[12] = base_mid + [-0.09, -1.0, 0.0]
            set_finger(13, extended=False)
            set_finger(17, extended=False)
            pts[4] = [-0.1, -0.5, 0.0]
        elif gesture == "PLEASE":
            set_thumb(extended=False)
            set_finger(5, extended=True, spread_x=-0.02)
            set_finger(9, extended=True, spread_x=0.0)
            set_finger(13, extended=True, spread_x=0.02)
            set_finger(17, extended=True, spread_x=0.04)
            pts[4] = [-0.15, -0.6, 0.0]
        elif gesture == "WATER":
            set_thumb(extended=False)
            set_finger(5, extended=True, spread_x=-0.2)
            set_finger(9, extended=True, spread_x=0.0)
            set_finger(13, extended=True, spread_x=0.2)
            set_finger(17, extended=False)
        elif gesture == "FOOD":
            set_thumb(extended=False)
            set_finger(5, extended=False, curl_y=0.0)
            set_finger(9, extended=False, curl_y=0.0)
            set_finger(13, extended=False, curl_y=0.0)
            set_finger(17, extended=False, curl_y=0.0)
            pinch_center = np.array([0.0, -0.9, 0.1])
            pts[4] = pinch_center + [-0.03, 0.0, 0.0]
            pts[8] = pinch_center + [-0.02, -0.03, 0.0]
            pts[12] = pinch_center + [0.0, -0.03, 0.0]
            pts[16] = pinch_center + [0.02, -0.03, 0.0]
            pts[20] = pinch_center + [0.03, 0.0, 0.0]
        elif gesture == "PAIN":
            set_thumb(extended=False)
            pts[3] = [-0.4, -0.4, 0.1]
            pts[4] = [-0.4, -0.3, 0.1]
            set_finger(5, extended=True, spread_x=0.0)
            set_finger(9, extended=False, curl_y=0.5)
            set_finger(13, extended=False, curl_y=0.5)
            set_finger(17, extended=False, curl_y=0.5)
        elif gesture == "DOCTOR":
            set_thumb(extended=False)
            set_finger(5, extended=True, spread_x=0.0)
            set_finger(9, extended=False)
            set_finger(13, extended=False)
            set_finger(17, extended=False)
            pts[4] = pts[12] + [-0.02, 0.01, 0.0]
        elif gesture == "PEACE":
            set_thumb(extended=False)
            set_finger(5, extended=True, spread_x=-0.25)
            set_finger(9, extended=True, spread_x=0.25)
            set_finger(13, extended=False)
            set_finger(17, extended=False)
        elif gesture == "I LOVE YOU":
            set_thumb(extended=True)
            set_finger(5, extended=True, spread_x=-0.1)
            set_finger(9, extended=False)
            set_finger(13, extended=False)
            set_finger(17, extended=True, spread_x=0.3)
        elif gesture == "OK":
            set_thumb(extended=False)
            set_finger(5, extended=False)
            pts[4] = [-0.15, -0.9, 0.0]
            pts[8] = [-0.15, -0.9, 0.0]
            set_finger(9, extended=True, spread_x=0.0)
            set_finger(13, extended=True, spread_x=0.15)
            set_finger(17, extended=True, spread_x=0.3)

        return pts

    def _build_and_train_model(self):
        X = []
        y = []
        rng = np.random.RandomState(42)

        for label_idx, gesture in enumerate(GESTURE_LABELS):
            base_pose = self._generate_synthetic_pose(gesture)
            for _ in range(60):
                noise = rng.normal(0, 0.03, base_pose.shape)
                perturbed = base_pose + noise
                feats = self.extract_features(perturbed)
                X.append(feats)
                y.append(label_idx)

        X = np.array(X)
        y = np.array(y)

        # KNeighborsClassifier: simple, fast and deterministic
        self.model = KNeighborsClassifier(n_neighbors=3, weights="distance")
        self.model.fit(X, y)

    def _check_two_hands(self, hand1_pts, hand2_pts):
        """Dono haath screen pe hain toh check karo if Namaste or double gesture ban raha hai."""
        h1 = np.array(hand1_pts, dtype=float)
        h2 = np.array(hand2_pts, dtype=float)

        # Distance between both wrists and middle fingertips
        dist_wrists = np.linalg.norm(h1[0] - h2[0])
        dist_tips = np.linalg.norm(h1[12] - h2[12])

        # Are both hands pointing up? (In screen coords, smaller y means higher up)
        fingers_pointing_up = (h1[12][1] < h1[0][1]) and (h2[12][1] < h2[0][1])

        # Namaste check: dono haath paas mein jude hue aur ungliyan upar
        if dist_wrists < 0.28 and dist_tips < 0.22 and fingers_pointing_up:
            return "NAMASTE", 0.98

        return None, 0.0

    def _heuristic_check(self, pts):
        """Hard geometric boundaries for guaranteed instant response without jitter."""
        d0_4 = np.linalg.norm(pts[4])
        d0_8 = np.linalg.norm(pts[8])
        d0_12 = np.linalg.norm(pts[12])
        d0_16 = np.linalg.norm(pts[16])
        d0_20 = np.linalg.norm(pts[20])

        ext_index = d0_8 > (np.linalg.norm(pts[6]) * 1.15)
        ext_middle = d0_12 > (np.linalg.norm(pts[10]) * 1.15)
        ext_ring = d0_16 > (np.linalg.norm(pts[14]) * 1.15)
        ext_pinky = d0_20 > (np.linalg.norm(pts[18]) * 1.15)
        ext_thumb = d0_4 > 0.8

        d_thumb_index = np.linalg.norm(pts[4] - pts[8])
        d_thumb_middle = np.linalg.norm(pts[4] - pts[12])
        tips = pts[[4, 8, 12, 16, 20]]
        tip_dispersion = np.mean([np.linalg.norm(t - np.mean(tips, axis=0)) for t in tips])

        # Food pinch: paancho ungliyan ek saath judi hui
        if tip_dispersion < 0.12 and d_thumb_index < 0.2 and d_thumb_middle < 0.2:
            return "FOOD", 0.96

        # OK sign: thumb aur index milkar circle banate hain aur baaki teen ungliyan upar
        if d_thumb_index < 0.28 and ext_middle and ext_ring and ext_pinky:
            return "OK", 0.96

        # I Love You: Thumb, Index, Pinky teen ungliyan open
        if ext_thumb and ext_index and not ext_middle and not ext_ring and ext_pinky:
            return "I LOVE YOU", 0.96

        # Peace vs NO:
        if ext_index and ext_middle and not ext_ring and not ext_pinky:
            d_index_middle = np.linalg.norm(pts[8] - pts[12])
            if d_index_middle > 0.3:
                return "PEACE", 0.96
            else:
                return "NO", 0.95

        # Water: W gesture (index, middle, ring teen ungliyan upar)
        if ext_index and ext_middle and ext_ring and not ext_pinky and not ext_thumb:
            return "WATER", 0.94

        # Yes: Thumbs up gesture
        if ext_thumb and not ext_index and not ext_middle and not ext_ring and not ext_pinky:
            if pts[4][1] < pts[2][1]:
                return "YES", 0.95

        # Doctor vs Pain:
        if ext_index and not ext_middle and not ext_ring and not ext_pinky:
            if d_thumb_middle < 0.35:
                return "DOCTOR", 0.94
            else:
                return "PAIN", 0.93

        # Hello: Saari 5 ungliyan open
        if ext_thumb and ext_index and ext_middle and ext_ring and ext_pinky:
            return "HELLO", 0.97

        return None, 0.0

    def _check_body_anchored_gestures(self, raw_pts, body_landmarks, secondary_pts=None):
        """
        Body landmarks (Head, Nose, Mouth/Lips, Neck, Chest, Shoulders) ke reference se
        physical touch aur proximity detection karte hain.
        Jaise: Fingers touching lips -> Water/Food/Thank You; Hand on chest -> Please.
        """
        if not body_landmarks:
            return None, 0.0

        raw = np.array(raw_pts, dtype=float)
        wrist = raw[0][:2]
        thumb_tip = raw[4][:2]
        index_tip = raw[8][:2]
        middle_tip = raw[12][:2]
        ring_tip = raw[16][:2]
        pinky_tip = raw[20][:2]
        palm_center = (wrist + raw[9][:2]) / 2.0

        # Body coordinates extract kar rahe hain
        chest = np.array(body_landmarks["chest"][:2], dtype=float) if "chest" in body_landmarks and body_landmarks["chest"] else None
        mouth = np.array(body_landmarks["mouth"][:2], dtype=float) if "mouth" in body_landmarks and body_landmarks["mouth"] else None
        nose = np.array(body_landmarks["nose"][:2], dtype=float) if "nose" in body_landmarks and body_landmarks["nose"] else None
        neck = np.array(body_landmarks["neck"][:2], dtype=float) if "neck" in body_landmarks and body_landmarks["neck"] else None

        # Normalized coordinates for finger extension check
        norm_pts = self._normalize_landmarks(raw_pts)
        ext_thumb = np.linalg.norm(norm_pts[4]) > 0.75
        ext_index = np.linalg.norm(norm_pts[8]) > (np.linalg.norm(norm_pts[6]) * 1.05)
        ext_middle = np.linalg.norm(norm_pts[12]) > (np.linalg.norm(norm_pts[10]) * 1.05)
        ext_ring = np.linalg.norm(norm_pts[16]) > (np.linalg.norm(norm_pts[14]) * 1.05)
        ext_pinky = np.linalg.norm(norm_pts[20]) > (np.linalg.norm(norm_pts[18]) * 1.05)

        tips = norm_pts[[4, 8, 12, 16, 20]]
        tip_dispersion = np.mean([np.linalg.norm(t - np.mean(tips, axis=0)) for t in tips])

        # 1. PLEASE: Flat open hand placed on the CHEST
        if chest is not None:
            dist_palm_chest = np.linalg.norm(palm_center - chest)
            dist_wrist_chest = np.linalg.norm(wrist - chest)
            # Palm ya wrist chest ke paas hai (< 0.24 screen distance)
            if min(dist_palm_chest, dist_wrist_chest) < 0.24:
                # Agar haath band mutthi (fist) nahi hai, toh chest pe haath = PLEASE
                is_fist = (not ext_index) and (not ext_middle) and (not ext_ring) and (not ext_pinky)
                if not is_fist:
                    return "PLEASE", 0.99

        # 2. GESTURES TOUCHING THE LIPS / MOUTH / CHIN
        if mouth is not None:
            dist_index_mouth = np.linalg.norm(index_tip - mouth)
            dist_middle_mouth = np.linalg.norm(middle_tip - mouth)
            dist_tips_mouth = min(dist_index_mouth, dist_middle_mouth)
            dist_palm_mouth = np.linalg.norm(palm_center - mouth)

            # A. FOOD: Pinch shape (all fingertips together) at mouth
            if dist_tips_mouth < 0.18 and tip_dispersion < 0.22:
                return "FOOD", 0.98

            # B. WATER: 'W' shape (Index, Middle, Ring up) touching lips/chin
            if (dist_tips_mouth < 0.20 or dist_palm_mouth < 0.24) and ext_index and ext_middle and ext_ring and not ext_pinky:
                return "WATER", 0.98

            # C. THANK YOU: Flat hand touching lips/chin and moving outwards
            if dist_tips_mouth < 0.18 and ext_index and ext_middle:
                return "THANK YOU", 0.98

        # 3. DOCTOR: Touching wrist of opposite hand, or neck/pulse check
        if secondary_pts is not None and len(secondary_pts) == 21:
            sec_wrist = np.array(secondary_pts[0][:2], dtype=float)
            dist_touch_sec = min(np.linalg.norm(index_tip - sec_wrist), np.linalg.norm(middle_tip - sec_wrist))
            if dist_touch_sec < 0.20 and ext_index:
                return "DOCTOR", 0.98

        if neck is not None:
            dist_neck = np.linalg.norm(palm_center - neck)
            if dist_neck < 0.18 and ext_index and not ext_ring and not ext_pinky:
                return "DOCTOR", 0.96

        # 4. HELLO: Open palm raised at head / temple level
        if nose is not None or chest is not None:
            ref_y = nose[1] if nose is not None else (chest[1] - 0.18)
            if palm_center[1] < (ref_y + 0.08) and ext_thumb and ext_index and ext_middle and ext_ring and ext_pinky:
                return "HELLO", 0.98

        return None, 0.0

    def predict(self, landmarks, secondary_landmarks=None, body_landmarks=None):
        if landmarks is None or len(landmarks) != 21:
            return {"gesture": "NO_HAND", "confidence": 0.0, "stable_gesture": "NO_HAND"}

        # 1. Dual-hand check (Namaste: dono haath screen pe hain aur jud rahe hain)
        if secondary_landmarks is not None and len(secondary_landmarks) == 21:
            two_hand_res, two_hand_conf = self._check_two_hands(landmarks, secondary_landmarks)
            if two_hand_res:
                self.history.append(two_hand_res)
                return {
                    "gesture": two_hand_res,
                    "confidence": two_hand_conf,
                    "stable_gesture": two_hand_res
                }

        # 2. Body-anchored gestures check (Lips, Chest, Neck, Head)
        if body_landmarks:
            body_gesture, body_conf = self._check_body_anchored_gestures(landmarks, body_landmarks, secondary_landmarks)
            if body_gesture:
                self.history.append(body_gesture)
                return {
                    "gesture": body_gesture,
                    "confidence": body_conf,
                    "stable_gesture": body_gesture
                }

        # 3. Single hand classification
        pts = self._normalize_landmarks(landmarks)

        # First check deterministic geometric heuristics
        heuristic_gesture, heuristic_conf = self._heuristic_check(pts)
        if heuristic_gesture:
            raw_gesture = heuristic_gesture
            confidence = heuristic_conf
        else:
            # Fallback to trained KNN model on normalized feature vector
            feats = self.extract_features(pts).reshape(1, -1)
            pred_idx = self.model.predict(feats)[0]
            probs = self.model.predict_proba(feats)[0]
            raw_gesture = GESTURE_LABELS[pred_idx]
            confidence = round(float(probs[pred_idx]), 3)

        # Rolling majority voting (pichle 7 frames ka consensus lete hain)
        self.history.append(raw_gesture)
        counts = {}
        for g in self.history:
            counts[g] = counts.get(g, 0) + 1
        majority_gesture, majority_count = max(counts.items(), key=lambda item: item[1])

        if majority_count >= (len(self.history) // 2 + 1):
            stable_gesture = majority_gesture
        else:
            stable_gesture = self.history[-1]

        return {
            "gesture": raw_gesture,
            "confidence": confidence,
            "stable_gesture": stable_gesture
        }

sign_recognizer = SignRecognizer()
