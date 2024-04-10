import torch
import sys
from utils import AttnLabelConverter
from torchvision.transforms import ToTensor
from dataset import AlignCollate
from model import Model
from PIL import Image
import yaml
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def infer(model, image_path, opt):
    model.eval()
    converter = AttnLabelConverter(opt.character)
    AlignCollate_demo = AlignCollate(imgH=opt.imgH, imgW=opt.imgW, keep_ratio_with_pad=opt.PAD)
    
    if opt.rgb:
        image = Image.open(image_path).convert('RGB')
    else: 
        image = Image.open(image_path).convert('L')  # Convert to grayscale if necessary

    # We must provide a list of (image, None) pairs
    # AlignCollate expects tuples, so we wrap our image with (image, None)
    image_tensor, _ = AlignCollate_demo([(image, None)])
    image_tensor = image_tensor.to(device)
    batch_size = image_tensor.size(0)
    text_for_pred = torch.zeros((1, opt.batch_max_length + 1), dtype=torch.long).to(device)
    length_for_pred = torch.IntTensor([opt.batch_max_length] * batch_size).to(device)

    with torch.no_grad():
        # Forward pass to get network predictions
        preds = model(image_tensor, text_for_pred, is_train=False)
        _, preds_index = preds.max(2)
        preds_str = converter.decode(preds_index.data, length_for_pred)
        # pred_str has padding of [s] at the end. Split and take out only prediction
        cleaned_preds = [pred.split('[s]', 1)[0] for pred in preds_str]
        return cleaned_preds[0]
    
def load_config(config_file):
    try:
        with open(config_file) as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error loading config file '{config_file}': {e}")
        sys.exit(1)
    


if __name__ == '__main__':
    '''
    model_config.yaml is all data generated from opt.txt file after training your custom dataset
    '''
    if len(sys.argv) < 3:
        print("Usage: python script.py <model_config.yaml> <image_path>")
        sys.exit(1)
    config_file = sys.argv[1]
    image_path = sys.argv[2]

    config = load_config(config_file)

    opt = type('', (object,), config)()
    opt.character = config['character']

    """ model configuration """
    converter = AttnLabelConverter(opt.character)
    opt.num_class = len(converter.character)

    # load model
    model = Model(opt)
    model = torch.nn.DataParallel(model).to(device)
    model.load_state_dict(torch.load(opt.saved_model, map_location=device))
    opt.exp_name = '_'.join(opt.saved_model.split('/')[1:])

    # Perform inference
    predicted_text = infer(model, image_path, opt)
    print(f'{predicted_text}')