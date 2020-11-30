import tensorflow as tf
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import glob
from utils import get_class_dict

image_paths = glob.glob('./data/hirise-map-proj-v3_2/unlabeled/*.jpg')
#image_paths = glob.glob('./data/hirise-map-proj-v3_2/labeled/*.jpg')
list_ds = tf.data.Dataset.list_files(image_paths)

process_fn = lambda x: \
    tf.cast(tf.image.resize(tf.tile(tf.io.decode_jpeg(tf.io.read_file(x)), [1, 1, 3]), [96, 96]), tf.float32) / 255
image_ds = list_ds.map(process_fn)
batched_ds = image_ds.batch(100)

# For MobileNetV2, input_shape can be 96, 128, 160, 192, 224
#                  alpha can be 0.35, 0,5, 0,75, 1, 1.3, 1.4
model = tf.keras.applications.MobileNetV2(alpha=0.35, input_shape=(96, 96, 3), include_top=False, pooling='avg')

for i, batch in enumerate(batched_ds):
    batch_input = tf.keras.applications.mobilenet_v2.preprocess_input(batch)
    batch_output = model(batch_input).numpy()
    if not i:
        output = batch_output
    else:
        output = np.vstack((output, batch_output))

output /= np.sum(output**2, axis=1, keepdims=True)**0.5
pca_model = PCA(n_components=10)
feats = pca_model.fit_transform(output)
feats /= np.sum(feats**2, axis=1, keepdims=True)**0.5
print(pca_model.explained_variance_ratio_, sum(pca_model.explained_variance_ratio_))
#feats = output

sil_scores = []
max_k = 10
for i in range(2, max_k):
    kmeans_model = KMeans(i)
    kmeans_model.fit(feats)
    cluster_assigns = kmeans_model.predict(feats)
    sil = silhouette_score(feats, cluster_assigns)
    sil_scores.append(sil)

plt.figure()
plt.plot(np.arange(2, max_k), sil_scores)
plt.show()

