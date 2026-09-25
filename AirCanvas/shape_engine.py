import cv2
import numpy as np

def recognize_shape(points):
    """
    Analyzes an array of (x, y) stroke points drawn by the user
    and detects if it resembles a basic geometric shape:
    - CIRCLE
    - RECTANGLE
    - TRIANGLE
    - LINE
    - FREEHAND (no match)
    """
    if not points or len(points) < 8:
        return {"shape": "FREEHAND", "confidence": 0.0}

    pts = np.array(points, dtype=np.float32)
    
    # Total path length (sum of distances between consecutive points)
    dists = np.sqrt(np.sum(np.diff(pts, axis=0)**2, axis=1))
    path_len = np.sum(dists)
    if path_len < 15:
        return {"shape": "FREEHAND", "confidence": 0.0}

    # Distance between start point and end point
    endpoint_dist = np.linalg.norm(pts[0] - pts[-1])
    is_closed = (endpoint_dist / (path_len + 1e-6)) < 0.25

    # 1. Test for Straight Line: endpoint distance is ~path length
    if endpoint_dist / (path_len + 1e-6) > 0.90:
        return {
            "shape": "LINE",
            "confidence": 0.95,
            "params": {
                "start": [float(pts[0][0]), float(pts[0][1])],
                "end": [float(pts[-1][0]), float(pts[-1][1])]
            }
        }

    # If it is closed, check Circle, Rectangle, Triangle
    if is_closed:
        contour = pts.reshape((-1, 1, 2)).astype(np.int32)
        perimeter = cv2.arcLength(contour, closed=True)
        area = cv2.contourArea(contour)

        if perimeter > 20 and area > 100:
            # Circularity metric: 4 * pi * Area / (Perimeter^2) -> 1.0 for perfect circle
            circularity = (4 * np.pi * area) / (perimeter ** 2 + 1e-6)
            
            # (x, y), radius of minimum enclosing circle
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            circle_area = np.pi * (radius ** 2)
            area_ratio = area / (circle_area + 1e-6)

            if circularity > 0.68 or area_ratio > 0.65:
                return {
                    "shape": "CIRCLE",
                    "confidence": round(float(circularity), 2),
                    "params": {
                        "center": [float(cx), float(cy)],
                        "radius": float(radius)
                    }
                }

            # Test for Polygon (Triangle, Rectangle)
            epsilon = 0.04 * perimeter
            approx = cv2.approxPolyDP(contour, epsilon, closed=True)
            num_vertices = len(approx)

            if num_vertices == 3:
                vertices = approx.reshape(-1, 2).tolist()
                return {
                    "shape": "TRIANGLE",
                    "confidence": 0.88,
                    "params": {
                        "vertices": vertices
                    }
                }
            elif num_vertices == 4:
                # Bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                return {
                    "shape": "RECTANGLE",
                    "confidence": 0.90,
                    "params": {
                        "x": float(x),
                        "y": float(y),
                        "width": float(w),
                        "height": float(h),
                        "is_square": 0.85 <= aspect_ratio <= 1.15
                    }
                }

    return {"shape": "FREEHAND", "confidence": 0.0}
