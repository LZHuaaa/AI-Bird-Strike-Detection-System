"""# bird_communication_system/audio_analysis.py
import torch, torch.nn as nn, numpy as np, pickle, librosa
from torchvision import models

device = torch.device("cpu")
le = pickle.load(open("label_encoder.pkl", "rb"))
num_classes = len(le.classes_)

classifier_model = models.efficientnet_b0(pretrained=False)
classifier_model.classifier[1] = nn.Linear(classifier_model.classifier[1].in_features, num_classes)
classifier_model.load_state_dict(torch.load("bird_classifier.pth", map_location=device))
classifier_model.eval()

def classify_audio_segment(segment, sr=32000):
    S = librosa.feature.melspectrogram(y=segment, sr=sr, n_mels=128)
    S_DB = librosa.power_to_db(S, ref=np.max)
    target_size = (128, 256)
    if S_DB.shape[1] < target_size[1]:
        S_DB = np.pad(S_DB, ((0, 0), (0, target_size[1] - S_DB.shape[1])))
    else:
        S_DB = S_DB[:, :target_size[1]]
    spec = np.stack([S_DB] * 3, axis=0)
    spec_tensor = torch.tensor(spec, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        outputs = classifier_model(spec_tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        top_prob, top_idx = torch.max(probs, 0)

    if top_prob.item() > 0.5:
        return le.classes_[top_idx.item()], top_prob.item()
    return None, None """
