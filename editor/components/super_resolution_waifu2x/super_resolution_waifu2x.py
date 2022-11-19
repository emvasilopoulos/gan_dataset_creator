from editor.component import Component
from editor.components.waifu2x.utils.prepare_images import *
from editor.components.waifu2x.Models import *
from torchvision.utils import make_grid
import torchvision
import torch
import cv2

class SuperResolutionWaifu2x(Component):

    def __init__(self, checkpoint, input_frame_shape) -> None:
        if torch.cuda.is_available():
            self.device = 'cuda:0'
        else:
            self.device = 'cpu'

        model_cran_v2 = CARN_V2(color_channels=3, mid_channels=64, conv=torch.nn.Conv2d,
                                single_conv_size=3, single_conv_group=1,
                                scale=2, activation=torch.nn.LeakyReLU(0.1),
                                SEBlock=True, repeat_blocks=3, atrous=(1, 1, 1))

        model_cran_v2 = network_to_whole(model_cran_v2)
        model_cran_v2.load_state_dict(torch.load(checkpoint, map_location=self.device))

        # if use GPU, then comment out the next line so it can use fp16.
        #self.model_cran_v2 = model_cran_v2.float()
        self.model_cran_v2 = model_cran_v2
        self.TRANSFORM_IMG = torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Resize(input_frame_shape),
            torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225])
        ])

        # overlapping split
        # if input image is too large, then split it into overlapped patches
        # details can be found at [here](https://github.com/nagadomi/waifu2x/issues/238)
        self.img_splitter = ImageSplitter(seg_size=64, scale_factor=2, boarder_pad_size=3, device=self.device)

    def edit(self, frame, *kwargs):
        # You may need to convert the color.
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)

        """
        # origin
        if self.device == 'cpu':
            img_t = to_tensor(im_pil).unsqueeze(0)
        else:
            img_t = to_tensor(im_pil).unsqueeze(0).to('cuda:0')
        """
        # used to compare the origin
        img = im_pil.resize((im_pil.size[0] // 2, im_pil.size[1] // 2), Image.Resampling.BICUBIC)

        img_patches = self.img_splitter.split_img_tensor(img, scale_method=None, img_pad=0)
        with torch.no_grad():
            out = [self.model_cran_v2(patch) for patch in img_patches]
        img_upscale = self.img_splitter.merge_img_tensor(out)

        #final = torch.cat([img_t, img_upscale])
        grid = make_grid(img_upscale, nrow=2, padding=2, pad_value=0,
                         normalize=False, range=None, scale_each=False)
        # Add 0.5 after unnormalizing to [0, 255] to round to nearest integer
        ndarr = grid.mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to('cpu', torch.uint8).numpy()
        final_img = cv2.cvtColor(ndarr, cv2.COLOR_RGB2BGR)
        return final_img

    def get_component_name(self) -> str:
        return "SuperResolutionWaifu2x"


if __name__ == '__main__':

    checkpoint_path = "./model_check_points/CRAN_V2/CARN_model_checkpoint.pt"
    super_resolution = SuperResolutionWaifu2x(checkpoint_path, (720, 880))
    cap = cv2.VideoCapture(
        'D:/Downloads Google Chrome/SILVER SURFER - The Complete ANIMATED Series (1998) - 720p Web-DL x264/season_1_episode_1.mp4')
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret and i >=2000:
            # Custom shape for Silver surfer
            frame = frame[:, 200:1080]
            final = super_resolution.edit(frame)
            img = cv2.cvtColor(final, cv2.COLOR_RGB2BGR)
            cv2.imwrite(f'./output_examples/out_{i}.png', img)
            print(f'Saved frame #{i}')
        i += 1
