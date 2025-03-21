import glob
import os

import cv2
import numpy as np
import sklearn
import streamlit as st


def app():
    st.title("たべっ子水族館へようこそ！")

    image_path = st.text_input("画像ディレクトリ", "/datasets/tabekko_suizokukan/images/250314a")
    image_paths = sorted(glob.glob(os.path.join(image_path, '*.jpg')))
    image_index = st.sidebar.number_input(
        "イメージ番号", min_value=0, max_value=len(image_paths) - 1
    )
    image_path = image_paths[image_index]
    image = cv2.imread(image_path)

    pixels = image.reshape(-1, 3)

    binarization_method = st.sidebar.radio(
        "バイナリ化手法", ["k-means", "otsu", "adaptive", "manual"], index=3
    )

    if binarization_method == "k-means":
        model = sklearn.cluster.KMeans(n_clusters=2)
        model.fit(pixels)
        labels = model.predict(pixels)
        mask = labels.reshape(image.shape[:2])
        mask = mask.astype(np.uint8) * 255
    elif binarization_method == "otsu":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif binarization_method == "adaptive":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    elif binarization_method == "manual":
        threshold = st.sidebar.slider("閾値", min_value=0, max_value=255, value=128)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        mask = cv2.bitwise_not(mask)

    # オープニング処理でノイズを除去
    kernel_size = st.sidebar.slider(
        "カーネルサイズ", min_value=1, max_value=50, value=5
    )
    mask = cv2.morphologyEx(
        mask, cv2.MORPH_OPEN, kernel=np.ones((kernel_size, kernel_size))
    )

    columns = st.columns(2)
    columns[0].image(
        image, channels="BGR", caption=f"たべっ子水族館の画像: {image_index}"
    )
    columns[1].image(mask, caption="二値化の結果")


if __name__ == "__main__":
    app()
