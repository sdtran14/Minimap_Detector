import torchimport cv2import numpy as npimport osimport glob as globfrom xml.etree import ElementTree as etfrom config import CLASSES, RESIZE_TO, TRAIN_DIR, VALID_DIR, BATCH_SIZEfrom torch.utils.data import Dataset, DataLoaderfrom utils import collate_fn, get_train_transform, get_valid_transformclass MinimapDataset(Dataset):    def __init__(self, dir_path, width, height, classes, transforms=None):        self.transforms = transforms        self.dir_path = dir_path        self.height = height        self.width = width        self.classes = classes                # get all the image paths in sorted order        self.image_paths = glob.glob(f"{self.dir_path}/*.png")        self.all_images = [image_path.split('/')[-1] for image_path in self.image_paths]        self.all_images = sorted(self.all_images)        def __getitem__(self,idx):        image_name = self.all_images[idx]        image_path = os.path.join(self.dir_path, image_name)                image = cv2.imread(image_path)        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) #converts bgr to rgb if needed        image = image.astype(np.float32)        image_resized = cv2.resize(image, (self.width, self.height))        image_resized /= 255.0        annot_filename = image_name[:-4] + '.xml' #:-4 means ignore last 4 characteres in string        annot_file_path = os.path.join(self.dir_path, annot_filename)                boxes = []        labels = []        tree = et.parse(annot_file_path)        root = tree.getroot()        image_width = image.shape[1]        image_height = image.shape[0]                #Start parsing annotation xml file        for member in root.findall('object'):            #box coordinates extracted and corrected for size            labels.append(self.classes.index(member.find('name').text))            #labels contain labels' indexes in the CLASSES                        #xmin = left corner x-coordinates            xmin = int(member.find('bndbox').find('xmin').text)            xmax = int(member.find('bndbox').find('xmax').text)            ymin = int(member.find('bndbox').find('ymin').text)            ymax = int(member.find('bndbox').find('ymax').text)                        xmin_final = (xmin/image_width)*self.width            xmax_final = (xmax/image_width)*self.width            ymin_final = (ymin/image_height)*self.width            ymax_final = (ymax/image_height)*self.width                        boxes.append([xmin_final, ymin_final, xmax_final, ymax_final])                    boxes = torch.as_tensor(boxes, dtype=torch.float32)        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])        iscrowd = torch.zeros((boxes.shape[0],), dtype=torch.int64)        labels = torch.as_tensor(labels, dtype=torch.int64)                target = {}        target["boxes"] = boxes        target["labels"] = labels        target["area"] = area        target["iscrowd"] = iscrowd        image_id = torch.tensor([idx])        target["image_id"] = image_id                if self.transforms:            sample = self.transforms(image = image_resized,                                     bboxes = target['boxes'],                                     labels = labels)            image_resized = sample['image']            target['boxes'] = torch.Tensor(sample['bboxes'])                    return image_resized, target        def __len__(self):        return len(self.all_images)    train_dataset = MinimapDataset(TRAIN_DIR, RESIZE_TO, RESIZE_TO, CLASSES, get_train_transform())valid_dataset = MinimapDataset(VALID_DIR, RESIZE_TO, RESIZE_TO, CLASSES, get_valid_transform())#dataLoader is imported from torchtrain_loader = DataLoader(train_dataset,                           batch_size = BATCH_SIZE,                          shuffle=True,                          num_workers = 0,                          collate_fn = collate_fn                          )valid_loader = DataLoader(valid_dataset,                           batch_size = BATCH_SIZE,                          shuffle=False,                          num_workers = 0,                          collate_fn = collate_fn                          )print(f"Number of training samples: {len(train_dataset)}")print(f"Number of validation samples: {len(valid_dataset)}\n")    # execute datasets.py using Python command from Terminal...# ... to visualize sample images# USAGE: python datasets.pydebug = False;    if __name__ == '__main__' or debug:   dataset = MinimapDataset(       TRAIN_DIR, RESIZE_TO, RESIZE_TO, CLASSES   )   print(f"Number of training images: {len(dataset)}")      def visualize_sample(image, target):       boxes = target['boxes']       labelIDs = target['labels']       #print(target['labels'])              for i in range(len(labelIDs)):            cv2.rectangle(               image,                (int(boxes[i][0]), int(boxes[i][1])), (int(boxes[i][2]), int(boxes[i][3])),               (0, 255, 0), 1           )           cv2.putText(               image, CLASSES[labelIDs[i]], (int(boxes[i][0]), int(boxes[i][1]-5)),                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2           )                  cv2.imshow('Image', image)       cv2.waitKey(0)          NUM_SAMPLES_TO_VISUALIZE = 1   for i in range(NUM_SAMPLES_TO_VISUALIZE):       image, target = dataset[i]       visualize_sample(image,target)                   