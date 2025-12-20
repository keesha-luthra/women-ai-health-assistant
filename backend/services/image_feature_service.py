import torch
from torchvision import models, transforms
from PIL import Image


class ImageFeatureService:
    """
    Uses a pretrained CNN as a frozen feature extractor.
    """

    def __init__(self):
        self.model = models.mobilenet_v2(pretrained=True)
        self.model.classifier = torch.nn.Identity()
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_features(self, image_path: str):
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            features = self.model(tensor)

        return features.squeeze().numpy()
