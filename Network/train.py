import enum
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils import data
import torchvision.transforms as transforms
from torch.utils.tensorboard.writer import SummaryWriter
from get_data import get_data
from model import CNNToRNN
from utils import save_checkpoint, load_checkpoint, print_examples
from tqdm import tqdm

def train():
    transform = transforms.Compose(
        [
            transforms.Resize((356, 356)),
            transforms.RandomCrop((299, 299)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ]
    )

    train_loader, dataset = get_data(
        image_dir="data/images", 
        image_loc="data/imageLoc.txt", 
        code="data/code.txt", 
        transform=transform,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    load_model = False
    save_model = True

    embed_size = 256
    hidden_size = 256
    vocab_size = len(dataset.vocab)
    num_layers = 1
    learning_rate = 3e-4
    num_epochs = 15

    writer = SummaryWriter("runs/flutter")
    step = 0

    model = CNNToRNN(embed_size, hidden_size, vocab_size, num_layers).to(device)
    cri = nn.CrossEntropyLoss(ignore_index=dataset.vocab.stoi["<PAD>"])
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    if load_model:
        step = load_checkpoint(torch.load("checkpoint.pth.tar"), model, optimizer)

    model.train()

    for epoch in range(num_epochs):
        # Uncomment the line below to see a couple of test cases
        # print_examples(model, device, dataset)

        if save_model:
            checkpoint = {
                "state_dict": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
            }
            save_checkpoint(checkpoint)

        for idx, (images, code) in enumerate(train_loader):
            images = images.to(device)
            code = code.to(device)

        outputs = model(images, code[:-1])
        loss = cri(
            outputs.reshape(-1, outputs.shape[2]), code.reshape(-1)
        )

        writer.add_scalar("Training loss", loss.item(), global_step=step)
        step += 1

        optimizer.zero_grad()
        loss.backward(loss)
        optimizer.step()

if __name__ == "__main__":
    train()