import torch
from torch.utils.data import dataset
from get_data import FlutterData, Vocabulary, Pad
import torchvision.transforms as transforms
import torch.nn as nn
import torchvision.models as models
from PIL import Image
import torch.optim as optim
import pickle
from model import CNNToRNN

transform = transforms.Compose(
    [
        transforms.Resize((356, 356)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ]
)

dataset = pickle.load(open("dataset.obj", "rb"))

embed_size = 256
hidden_size = 256
vocab_size = len(dataset.vocab)
num_layers = 1
learning_rate = 3e-4
num_epochs = 100

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = CNNToRNN(embed_size, hidden_size, vocab_size, num_layers).to(device)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

checkpoint = torch.load("checkpoint.pth.tar")

model.load_state_dict(checkpoint["state_dict"])
optimizer.load_state_dict(checkpoint["optimizer"])
model.eval()

test_img = transform(Image.open("test.png").convert("RGB"))
test_img = test_img.unsqueeze(0)

final_c = model.code_img(test_img.to(device), dataset.vocab)
print(final_c)