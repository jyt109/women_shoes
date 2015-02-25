import scipy
from scipy import ndimage
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
import os
import sys


if __name__ == '__main__':
    file_names = os.listdir('shoes')

    target_lst = []
    feature_arr = None
    for file_name in file_names:
        print file_name
        if file_name.startswith('pump'):
            label = 1
        elif file_name.startswith('flat'):
            label = 0
        else:
            continue
        target_lst.append(label)

        img_arr = scipy.misc.imread('shoes/%s' % file_name).astype('int32')
        dx = ndimage.sobel(img_arr, 0)  # horizontal derivative
        dy = ndimage.sobel(img_arr, 1)  # vertical derivative
        mag = np.hypot(dx, dy)  # magnitude
        mag *= 255.0 / np.max(mag)  # normalize (Q&D)
        print mag
        print mag.shape
        sys.exit()

        img_arr = mag.flatten()[np.newaxis, :]

        if feature_arr is None:
            feature_arr = img_arr
        else:
            feature_arr = np.r_[feature_arr, img_arr]

    target_arr = np.array(target_lst)

    train_feat, test_feat, train_target, test_target = train_test_split(feature_arr, target_arr, test_size=0.33)
    rf = RandomForestClassifier()
    rf.fit(train_feat, train_target)
    print rf.score(test_feat, test_target)

