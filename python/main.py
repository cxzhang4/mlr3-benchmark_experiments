import torch
import torch.nn as nn 
import torchvision.transforms as transforms
from data import GuessTheCorrelationDataset
import time
import custom_transforms
from model import create_learner
import hydra

@hydra.main(version_base=None, config_path=".", config_name="config")
def main(config):
    # create a torch dataset
    transforms_for_corr_images = transforms.Compose([
        custom_transforms.CustomCrop(top = 0, left = 21, height = 130, width = 130),
        # custom_transforms.AddChannelDimension()
    ])

    trn_idx = range(0, config.default.train_size)
    train_ds = GuessTheCorrelationDataset(root = "data/correlation/guess-the-correlation",
                                        responses_file_path = "train.csv",
                                        transform = transforms_for_corr_images,
                                        indexes = trn_idx)
    train_dataloader = torch.utils.data.DataLoader(train_ds, batch_size=config.default.batch_size)

    print(train_ds.__getitem__(0)[0].shape)
    # TODO: compute input_dim instead of hard-coding it
    # TODO: fix the transformations so that the true input dimension matches the hard-coded input dimension
    # input_dim = 16900
    # output_dim = 1
    learner = create_learner(config.default.architecture_id)

    DEVICE = config.default.accelerator
    learner = learner.to(DEVICE)

    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(learner.parameters(), lr = config.default.learning_rate)

    start_time = time.time()
    for i in range(config.default.n_epochs):
        learner.train()
        for i, (img, target) in enumerate(train_dataloader):
            print(img.shape)
            print(target.shape)
            img, target = img.to(DEVICE), target.to(DEVICE)

            optimizer.zero_grad()
            img = img.float()
            y_pred = learner(img)
            loss = loss_fn(torch.squeeze(y_pred), target.float())
            loss.backward()
            optimizer.step()
    end_time = time.time()

    print(end_time - start_time)

if __name__ == "__main__":
    main()