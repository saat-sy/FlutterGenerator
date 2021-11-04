import os
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import MWETokenizer
import torchvision.transforms as transforms
import pickle

nlp = spacy.load("en_core_web_sm")
# nltk.download('punkt')

tokenizer = MWETokenizer([('<', 'N', '>')])

class Vocabulary:
    def __init__(self, freq_threshold):
        self.itos = {0:"<PAD>", 1:"<SOS>", 2:"<EOS>", 3:"<N>", 4:"<UNK>"}
        self.stoi = {"<PAD>":0, "<SOS>":1, "<EOS>":2, "<N>":3, "<UNK>":4}
        self.freq_threshold = freq_threshold

    def __len__(self):
        return len(self.itos)

    @staticmethod
    def tokenizer_eng(code):
        # print([tok for tok in tokenizer.tokenize(word_tokenize(code))])
        return [tok for tok in tokenizer.tokenize(word_tokenize(code))]

    def build_vocab(self, code):
        frequencies = {}
        idx = 5

        for codeFile in code:
            for word in self.tokenizer_eng(codeFile):
                if word not in frequencies:
                    frequencies[word] = 1
                
                else:
                    frequencies[word] += 1
                
                if frequencies[word] == self.freq_threshold:
                    self.stoi[word] = idx
                    self.itos[idx] = word
                    idx += 1

    def numericalize(self, code):
        tokenized_text = self.tokenizer_eng(code)

        # return index of the each word from the dict or index of unknown if it ain't available
        return [
            self.stoi[token] if token in self.stoi else self.stoi["<UNK>"] 
            for token in tokenized_text
        ]

class FlutterData(Dataset):
    def __init__(self, image_dir, image_loc, code_loc, transform=None, freq_threshold=1):
        self.image_dir = image_dir
        
        imgs = open(image_loc, 'r').readlines()
        new_imgs = []
        for img in imgs:
            new_imgs.append(img.replace('\n', ''))

        self.images = new_imgs
        self.code = open(code_loc, 'r').readlines()
        self.transform = transform

        # VOCAB
        self.vocab = Vocabulary(freq_threshold)
        self.vocab.build_vocab(self.code)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        code = self.code[index]
        image_id = self.images[index]

        image = Image.open(image_id).convert("RGB")

        if self.transform is not None:
            image = self.transform(image)

        num_code = [self.vocab.stoi["<SOS>"]]
        num_code += self.vocab.numericalize(code)
        num_code.append(self.vocab.stoi["<EOS>"])

        return image, torch.tensor(num_code)

class Pad:
    def __init__(self, pad_idx):
        # INDEX OF <PAD> IN STOI -> NEEDED TO PAD 
        self.pad_idx = pad_idx

    def __call__(self, batch):
        images = [item[0].unsqueeze(0) for item in batch]
        images = torch.cat(images, dim=0)

        code = [item[1] for item in batch]
        code = pad_sequence(code, batch_first=False, padding_value=self.pad_idx)

        return images, code

def get_data(
    image_dir,
    image_loc,
    code,
    transform,
    batch_size=32,
    num_workers=8,
    shuffle=True,
    pin_memory=True
):
    dataset = FlutterData(image_dir, image_loc, code, transform)

    pad_idx = dataset.vocab.stoi["<PAD>"]

    loader = DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=shuffle,
        pin_memory=pin_memory,
        collate_fn=Pad(pad_idx),
    )

    file_data = open('dataset.obj', 'wb') 
    pickle.dump(dataset, file_data)

    return loader, dataset

def main():
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )
    dataloader, _ = get_data("data/images", "data/imageLoc.txt", "data/code.txt", transform=transform)

    for idx, (images, code) in enumerate(dataloader):
        print(images.shape)
        print(code.shape)

if __name__ == "__main__":
    main()