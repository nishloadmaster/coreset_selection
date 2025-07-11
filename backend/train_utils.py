import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms

class SimpleDataset(Dataset):
    def __init__(self, path):
        self.dataset = datasets.FakeData(transform=transforms.ToTensor())  # placeholder for your dataset loader

    def __getitem__(self, index):
        return self.dataset[index]

    def __len__(self):
        return len(self.dataset)

def load_dataset(path):
    return SimpleDataset(path)

def load_model(model_path):
    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(3*224*224, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    return model

def evaluate_model(model, dataset):
    loader = DataLoader(dataset, batch_size=16)
    criterion = nn.CrossEntropyLoss()
    correct = 0
    total = 0
    total_loss = 0
    model.eval()
    with torch.no_grad():
        for inputs, targets in loader:
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
    accuracy = correct / total
    avg_loss = total_loss / len(loader)
    return {"accuracy": accuracy, "loss": avg_loss}

def train_model(model, train_dataset, epochs=1, batch_size=16, lr=1e-4, device='cuda' if torch.cuda.is_available() else 'cpu'):
    dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    model = model.to(device)
    model.train()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        epoch_loss = 0.0
        for inputs, targets in dataloader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss / len(dataloader):.4f}")

    return model
