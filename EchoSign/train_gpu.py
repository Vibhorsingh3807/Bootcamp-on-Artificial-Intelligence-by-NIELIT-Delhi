import os
import sys
import time
import json
import argparse

# Ensure UTF-8 stdout for Windows consoles
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import datasets, transforms
import torchvision.models as models

# -------------------------------------------------------------
# Deep Learning Sign Language Classifier for NVIDIA RTX 4060
# Residual CNN model jo hand images ko 29 ASL classes mein classify karega
# -------------------------------------------------------------

class ASLResNet(nn.Module):
    """
    Ekdum lightweight aur super-fast Residual CNN.
    Total ~1.2 Million parameters hain, so RTX 4060 GPU pe < 2ms mein inference deta hai!
    """
    def __init__(self, num_classes=29):
        super(ASLResNet, self).__init__()
        
        # Stage 1: Basic features extract karna (Edges, corners, lines)
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )
        
        # Stage 2: Residual Block (Skip connection se gradient vanishing ki problem solve hoti hai)
        self.block1 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
        )
        self.downsample1 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=1, stride=2, bias=False),
            nn.BatchNorm2d(64)
        )
        self.relu1 = nn.ReLU(inplace=True)
        
        # Stage 3: Residual Block 64 -> 128
        self.block2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(128),
        )
        self.downsample2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=1, stride=2, bias=False),
            nn.BatchNorm2d(128)
        )
        self.relu2 = nn.ReLU(inplace=True)

        # Stage 4: Residual Block 128 -> 256
        self.block3 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(256)
        )
        self.downsample3 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=1, stride=2, bias=False),
            nn.BatchNorm2d(256)
        )
        self.relu3 = nn.ReLU(inplace=True)

        # Global Pooling and Classifier Head
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        out = self.conv1(x)
        
        res = self.downsample1(out)
        out = self.relu1(self.block1(out) + res)
        
        res = self.downsample2(out)
        out = self.relu2(self.block2(out) + res)
        
        res = self.downsample3(out)
        out = self.relu3(self.block3(out) + res)
        
        out = self.avgpool(out)
        out = torch.flatten(out, 1)
        out = self.dropout(out)
        out = self.fc(out)
        return out


def find_dataset_dir():
    candidates = [
        os.path.join(os.path.dirname(__file__), "DATASETS (2)", "asl_alphabet_train", "asl_alphabet_train"),
        os.path.join(os.path.dirname(__file__), "DATASETS", "Train_Alphabet"),
        os.path.join("EchoSign", "DATASETS (2)", "asl_alphabet_train", "asl_alphabet_train"),
        os.path.join("EchoSign", "DATASETS", "Train_Alphabet")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def train_model(epochs=6, batch_size=128, lr=1e-3, samples_per_class=350, full_dataset=False):
    # 1. Device Setup (NVIDIA RTX 4060 GPU Acceleration)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 65)
    print("  🚀 EchoSign AI — High-Performance Deep Learning Model Training")
    print(f"  ⚡ Hardware Device: {device}")
    if device.type == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"  🎮 GPU Name: {gpu_name} ({vram_gb:.1f} GB VRAM)")
        print(f"  ⚡ CUDA Capability: {torch.cuda.get_device_capability(0)}")
        torch.backends.cudnn.benchmark = True
    else:
        print("  ⚠️ CUDA not detected, falling back to CPU.")
    print("=" * 65)

    data_dir = find_dataset_dir()
    if not data_dir:
        print("❌ Error: Dataset directory not found!")
        return

    print(f"📁 Loading dataset from: {data_dir}")

    # 2. Data Transforms with GPU-friendly sizing & gentle spatial augmentations
    train_transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    full_dataset_obj = datasets.ImageFolder(data_dir, transform=train_transform)
    classes = full_dataset_obj.classes
    num_classes = len(classes)
    print(f"✅ Found {len(full_dataset_obj)} total images across {num_classes} classes: {classes[:8]} ... {classes[-4:]}")

    # Subsample if not training on all 87,000 images for rapid convergence
    if not full_dataset and samples_per_class:
        indices = []
        class_counts = {c: 0 for c in range(num_classes)}
        for idx, (_, label) in enumerate(full_dataset_obj.samples):
            if class_counts[label] < samples_per_class:
                indices.append(idx)
                class_counts[label] += 1
        active_dataset = Subset(full_dataset_obj, indices)
        print(f"📊 Training subset created: {len(active_dataset)} images ({samples_per_class} per class)")
    else:
        active_dataset = full_dataset_obj
        print(f"📊 Using full dataset: {len(active_dataset)} images")

    # Split train/validation (85% / 15%)
    val_size = int(len(active_dataset) * 0.15)
    train_size = len(active_dataset) - val_size
    train_ds, val_ds = random_split(active_dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        pin_memory=(device.type == "cuda"),
        num_workers=0
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        pin_memory=(device.type == "cuda"),
        num_workers=0
    )

    # 3. Model Architecture & Optimization
    model = ASLResNet(num_classes=num_classes).to(device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"🧠 Neural Architecture: ASLResNet ({total_params:,} trainable parameters)")

    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    scaler = torch.amp.GradScaler('cuda', enabled=(device.type == "cuda"))

    # 4. Training Loop with Mixed Precision
    print("\n🏋️ Starting GPU Training Loop...")
    start_time = time.time()
    best_val_acc = 0.0

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device, non_blocking=True), targets.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast('cuda', enabled=(device.type == "cuda")):
                outputs = model(inputs)
                loss = criterion(outputs, targets)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        scheduler.step()
        train_loss = running_loss / total
        train_acc = (correct / total) * 100.0

        # Validation Step
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device, non_blocking=True), targets.to(device, non_blocking=True)
                with torch.amp.autocast('cuda', enabled=(device.type == "cuda")):
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)

                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_total += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()

        val_loss = val_loss / val_total
        val_acc = (val_correct / val_total) * 100.0
        epoch_time = time.time() - epoch_start

        # GPU Memory report
        gpu_mem = f"{torch.cuda.memory_allocated() / (1024**2):.1f}MB" if device.type == "cuda" else "N/A"
        print(f"  [Epoch {epoch:02d}/{epochs:02d}] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}% | "
              f"Time: {epoch_time:.1f}s | VRAM: {gpu_mem}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc

    total_time = time.time() - start_time
    print("=" * 65)
    print(f"🎉 Training Complete in {total_time:.1f}s! Best Validation Accuracy: {best_val_acc:.2f}%")

    # 5. Save Artifacts
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)

    weights_path = os.path.join(models_dir, "asl_rtx4060.pt")
    classes_path = os.path.join(models_dir, "asl_classes.json")
    card_path = os.path.join(models_dir, "model_card.json")

    torch.save(model.state_dict(), weights_path)
    with open(classes_path, "w") as f:
        json.dump(classes, f, indent=2)

    model_card = {
        "model_architecture": "ASLResNet",
        "parameters": total_params,
        "input_resolution": [128, 128],
        "classes_count": num_classes,
        "classes": classes,
        "best_val_accuracy": round(best_val_acc, 2),
        "device_trained_on": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
        "training_time_seconds": round(total_time, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(card_path, "w") as f:
        json.dump(model_card, f, indent=2)

    print(f"💾 Saved Model Weights to: {weights_path}")
    print(f"💾 Saved Class Mappings to: {classes_path}")
    print(f"💾 Saved Model Card to:     {card_path}")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train EchoSign ASL Classifier on GPU")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=128, help="Batch size for training")
    parser.add_argument("--samples", type=int, default=350, help="Samples per class for rapid balanced training")
    parser.add_argument("--full", action="store_true", help="Train on the complete 87,000 image dataset")
    args = parser.parse_args()

    train_model(
        epochs=args.epochs,
        batch_size=args.batch_size,
        samples_per_class=args.samples,
        full_dataset=args.full
    )
