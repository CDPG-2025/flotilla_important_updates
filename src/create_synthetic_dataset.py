"""
Script to generate synthetic dataset for Flotilla
This creates the SYNTHETIC_IID dataset in the expected format
"""
import os
import torch
import yaml
from collections import Counter

def create_synthetic_dataset():
    """Create synthetic dataset partitions"""
    
    # Parameters
    num_train_samples = 5000
    num_test_samples = 1000
    num_classes = 10
    image_size = (3, 224, 224)
    dataset_name = "SYNTHETIC_IID"
    
    print(f"Generating synthetic dataset with {num_train_samples} train samples and {num_test_samples} test samples...")
    
    # Generate random training data
    train_data = torch.randn(num_train_samples, *image_size)
    train_labels = torch.randint(0, num_classes, (num_train_samples,))
    
    # Generate random test data
    test_data = torch.randn(num_test_samples, *image_size)
    test_labels = torch.randint(0, num_classes, (num_test_samples,))
    
    # Normalize the data
    train_data = (train_data - train_data.mean()) / train_data.std()
    test_data = (test_data - test_data.mean()) / test_data.std()
    
    # Create TensorDataset
    train_dataset = torch.utils.data.TensorDataset(train_data, train_labels)
    test_dataset = torch.utils.data.TensorDataset(test_data, test_labels)
    
    # Create DataLoaders
    trainloader = torch.utils.data.DataLoader(train_dataset, batch_size=1, shuffle=False)
    testloader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False)
    
    # Create directories
    train_dir = os.path.join("data", dataset_name)
    test_dir = os.path.join("val_data", dataset_name)
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Save training data
    train_file = os.path.join(train_dir, "train_data.pth")
    torch.save(trainloader, train_file)
    print(f"Saved training data to {train_file}")
    
    # Save test data
    test_file = os.path.join(test_dir, "test.pth")
    torch.save(testloader, test_file)
    print(f"Saved test data to {test_file}")
    
    # Calculate label distribution for training data
    label_counts = Counter(train_labels.tolist())
    label_distribution = {int(k): v / num_train_samples for k, v in label_counts.items()}
    
    # Create training dataset config
    train_config = {
        "dataset_details": {
            "data_filename": "train_data.pth",
            "dataset_id": dataset_name,
            "dataset_tags": ["IMAGE", "SYNTHETIC"],
            "suitable_models": ["LeNet5", "AlexNet", "FedAT_CNN"],
        },
        "metadata": {
            "label_distribution": label_distribution,
            "num_items": num_train_samples
        }
    }
    
    train_config_file = os.path.join(train_dir, "train_dataset_config.yaml")
    with open(train_config_file, "w") as f:
        yaml.dump(train_config, f, default_flow_style=False)
    print(f"Saved training config to {train_config_file}")
    
    # Calculate label distribution for test data
    test_label_counts = Counter(test_labels.tolist())
    test_label_distribution = {int(k): v / num_test_samples for k, v in test_label_counts.items()}
    
    # Create test dataset config
    test_config = {
        "dataset_details": {
            "data_filename": "test.pth",
            "dataset_id": dataset_name,
            "dataset_tags": ["IMAGE", "SYNTHETIC"],
            "suitable_models": ["LeNet5", "AlexNet", "FedAT_CNN"],
        },
        "metadata": {
            "label_distribution": test_label_distribution,
            "num_items": num_test_samples
        }
    }
    
    test_config_file = os.path.join(test_dir, "dataset_config.yaml")
    with open(test_config_file, "w") as f:
        yaml.dump(test_config, f, default_flow_style=False)
    print(f"Saved test config to {test_config_file}")
    
    print("\nSynthetic dataset created successfully!")
    print(f"Training data: {train_dir}/")
    print(f"Test data: {test_dir}/")
    print(f"\nLabel distribution (train): {label_distribution}")
    print(f"Label distribution (test): {test_label_distribution}")

if __name__ == "__main__":
    create_synthetic_dataset()
