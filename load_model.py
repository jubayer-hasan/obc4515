import os
import torch
from PIL import Image
from torchvision import transforms

INPUT_HEIGHT = 150
INPUT_WIDTH = 150
BATCH_SIZE = 8
VAL_SPLIT = 0.1
TEST_SPLIT = 0.1

resize = transforms.Resize(size=(INPUT_HEIGHT, INPUT_WIDTH))
hFlip = transforms.RandomHorizontalFlip(p=1)
vFlip = transforms.RandomVerticalFlip(p=1)
rotate = transforms.RandomRotation(degrees=15)


trainTransforms = transforms.Compose([resize, hFlip, vFlip, rotate,
                                      transforms.ToTensor()])
valTransforms = transforms.Compose([resize, transforms.ToTensor()])

idx2class = {0: 'Horizontal Error', 1: 'Vertical Error'}

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = torch.jit.load('model_scripted (2)500epoch.pt', device)


def predict(test_image_name):
    transform = transforms.Compose([resize, transforms.ToTensor()])
    test_image = Image.open(test_image_name)
    test_image_tensor = transform(test_image)
    if torch.cuda.is_available():
        test_image_tensor = test_image_tensor.view(1, 3, 150, 150).cuda()
    else:
        test_image_tensor = test_image_tensor.view(1, 3, 150, 150)
    with torch.no_grad():
        model.eval()
        out = model(test_image_tensor)
        ps = torch.exp(out)
        topk, topclass = ps.topk(1, dim=1)
        return idx2class[topclass.cpu().numpy()[0][0]]


# directory = './Error type 2'

# cnt1 = 0
# fls = '/content/drive/MyDrive/OBC-45/Horizontal Error/20220812_111211.jpg'
# for filename in os.scandir(directory):
#     if filename.is_file():
#         predict(filename.path)
#         cnt1 += 1
# print(cnt1)
