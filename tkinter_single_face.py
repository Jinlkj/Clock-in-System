import dlib
import numpy as np
import cv2
import os
import pandas as pd
import time
from PIL import Image, ImageDraw, ImageFont
import logging
from database_excution import *
from features_extraction_to_csv import main as main_features
import dlib
import numpy as np
import cv2
import os
import shutil
import time
import logging
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
# Dlib 正向人脸检测器 / Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()

# Dlib 人脸 landmark 特征点检测器 / Get face landmarks
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')

# Dlib Resnet 人脸识别模型, 提取 128D 的特征矢量 / Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")
class Punch_card:
    def __init__(self):
        self.name_cnt={}
        # Tkinter GUI
        self.win = tk.Tk()
        self.win.title("智能人脸打卡系统")

        # PLease modify window size here if needed
        self.win.geometry("800x412")

        # Tkinter left_part
        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        #Tkinter right_part
        self.frame_right_info = tk.Frame(self.win)
        self.label_current_name=tk.Label(self.frame_right_info,text="姓名")
        self.label_current_name_char=tk.Label(self.frame_right_info,text="unkown")
        self.last_name="unkown"
        self.current_name_char='unkown'
        self.log_all = tk.Label(self.frame_right_info)


        #fonts
        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=15, weight='bold')
        self.font_warning = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.cap = cv2.VideoCapture(0)  # Get video stream from camera

        self.reclassify_interval_cnt = 0
        self.reclassify_interval = 10

        self.face_name_known_list=[]
        self.features_known_list=[]
        self.last_frame_faces_cnt = 0
        self.current_frame_face_cnt = 0

        self.current_frame_face_position_list = []

        # Current frame and face ROI position
        self.current_frame = np.ndarray
        self.face_ROI_image = np.ndarray
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        # 用来存储当前帧检测出目标的名字 / List to save names of objects in current frame
        self.current_frame_name_list = []
    @staticmethod
    # 计算两个128D向量间的欧式距离 / Compute the e-distance between two 128D features
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist
    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (600, 412))
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            print("Error: No video input!!!")
    def get_face_database(self):
        if os.path.exists("data/features_all.csv"):
            path_features_known_csv = "data/features_all.csv"
            csv_rd = pd.read_csv(path_features_known_csv, header=None)
            for i in range(csv_rd.shape[0]):
                features_someone_arr = []
                self.face_name_known_list.append(csv_rd.iloc[i][0])
                for j in range(1, 129):
                    if csv_rd.iloc[i][j] == '':
                        features_someone_arr.append('0')
                    else:
                        features_someone_arr.append(csv_rd.iloc[i][j])
                self.features_known_list.append(features_someone_arr)
            #print(f"Faces in Database：{len(self.features_known_list)}",)
            return 1
        else:
            logging.warning("'features_all.csv' not found!")
            logging.warning("Please run 'get_faces_from_camera.py' "
                            "and 'features_extraction_to_csv.py' before 'face_reco_from_camera.py'")
            return 0
    def process(self):
        ret, self.current_frame = self.get_frame()
        if ret:
            # 2. 检测人脸 / Detect faces for frame X
            faces = detector(self.current_frame, 0)
            if len(faces) != 0:
                # 矩形框 / Show the ROI of faces
                for k, d in enumerate(faces):
                    self.face_ROI_width_start = d.left()
                    self.face_ROI_height_start = d.top()
                    # 计算矩形框大小 / Compute the size of rectangle box
                    self.face_ROI_height = (d.bottom() - d.top())
                    self.face_ROI_width = (d.right() - d.left())
                    self.hh = int(self.face_ROI_height / 2)
                    self.ww = int(self.face_ROI_width / 2)

                    # 判断人脸矩形框是否超出 480x640 / If the size of ROI > 480x640
                    if (d.right() + self.ww) > 1300 or (d.bottom() + self.hh > 700) or (d.left() - self.ww < 0) or (
                            d.top() - self.hh < 0):
                        color_rectangle = (255, 0, 0)
                    else:
                        color_rectangle = (255, 255, 255)
                    self.current_frame = cv2.rectangle(self.current_frame,
                                                       tuple([d.left() - self.ww, d.top() - self.hh]),
                                                       tuple([d.right() + self.ww, d.bottom() + self.hh]),
                                                       color_rectangle, 2)
            # 3. 更新帧中的人脸数 / Update cnt for faces in frames
            self.last_frame_faces_cnt = self.current_frame_face_cnt
            self.current_frame_face_cnt = len(faces)
            if self.current_frame_face_cnt == self.last_frame_faces_cnt:
                #print("scene 1: 当前帧和上一帧相比没有发生人脸数变化 / No face cnt changes in this frame!!!")

                if "unknown" in self.current_frame_name_list:
                    #print("   >>> 有未知人脸, 开始进行 reclassify_interval_cnt 计数")
                    self.reclassify_interval_cnt += 1

                # 4.1.1 当前帧一张人脸 / One face in this frame
                if self.current_frame_face_cnt == 1:
                    if self.reclassify_interval_cnt == self.reclassify_interval:
                        #print("  scene 1.1 需要对于当前帧重新进行人脸识别 / Re-classify for current frame")

                        self.reclassify_interval_cnt = 0
                        self.current_frame_face_feature_list = []
                        self.current_frame_face_X_e_distance_list = []
                        self.current_frame_name_list = []

                    for i in range(len(faces)):
                        shape = predictor(self.current_frame, faces[i])
                        self.current_frame_face_feature_list.append(
                            face_reco_model.compute_face_descriptor(self.current_frame, shape))

                        # a. 遍历捕获到的图像中所有的人脸 / Traversal all the faces in the database
                    for k in range(len(faces)):
                        self.current_frame_name_list.append("unknown")

                        # b. 每个捕获人脸的名字坐标 / Positions of faces captured
                        self.current_frame_face_position_list.append(tuple(
                            [faces[k].left(),
                             int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))

                        # c. 对于某张人脸, 遍历所有存储的人脸特征 / For every face detected, compare it with all the faces in the database
                        for i in range(len(self.features_known_list)):
                            # 如果 person_X 数据不为空 / If the data of person_X is not empty
                            if str(self.features_known_list[i][0]) != '0.0':
                                e_distance_tmp = self.return_euclidean_distance(
                                    self.current_frame_face_feature_list[k],
                                    self.features_known_list[i])
                                #print(f"    with person {i+1}, the e-distance: {e_distance_tmp}")
                                self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                            else:
                                # 空数据 person_X / For empty data
                                self.current_frame_face_X_e_distance_list.append(999999999)
                        # d. 寻找出最小的欧式距离匹配 / Find the one with minimum e distance
                        similar_person_num = self.current_frame_face_X_e_distance_list.index(
                            min(self.current_frame_face_X_e_distance_list))

                        if min(self.current_frame_face_X_e_distance_list) < 0.4:
                            # 在这里更改显示的人名 / Modify name if needed
                            # self.show_chinese_name()
                            self.current_frame_name_list[k] = self.face_name_known_list[similar_person_num]
                            #print(f"    recognition result for face {k+1}: {self.face_name_known_list[similar_person_num]}")
                            self.current_name_char=self.face_name_known_list[similar_person_num]
                        else:
                            print(f"    recognition result for face {k+1}: unkown")
                else:
                    # print("  scene 1.2 不需要对于当前帧重新进行人脸识别 / No re-classification needed for current frame")
                    # 获取特征框坐标 / Get ROI positions
                    for k, d in enumerate(faces):
                        # cv2.rectangle(self.current_frame,
                        #               tuple([d.left(), d.top()]),
                        #               tuple([d.right(), d.bottom()]),
                        #               (255, 255, 255), 2)
                        try:
                            self.current_frame_face_position_list[k] = tuple(
                                [faces[k].left(),
                                 int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)])
                        except:
                            print("两个人脸")
            # 4.2 当前帧和上一帧相比发生人脸数变化 / If face cnt changes, 1->0 or 0->1
            else:
                #print("scene 2: 当前帧和上一帧相比人脸数发生变化 / Faces cnt changes in this frame")
                self.current_frame_face_position_list = []
                self.current_frame_face_X_e_distance_list = []
                self.current_frame_face_feature_list = []

                # 4.2.1 人脸数从 0->1 / Face cnt 0->1
                if self.current_frame_face_cnt == 1:
                    #print("  scene 2.1 出现人脸, 进行人脸识别 / Get faces in this frame and do face recognition")
                    self.current_frame_name_list = []

                    for i in range(len(faces)):
                        shape = predictor(self.current_frame, faces[i])
                        self.current_frame_face_feature_list.append(
                            face_reco_model.compute_face_descriptor(self.current_frame, shape))

                    # a. 遍历捕获到的图像中所有的人脸 / Traversal all the faces in the database
                    for k in range(len(faces)):
                        self.current_frame_name_list.append("unknown")

                        # b. 每个捕获人脸的名字坐标 / Positions of faces captured
                        self.current_frame_face_position_list.append(tuple(
                            [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))

                        # c. 对于某张人脸, 遍历所有存储的人脸特征 / For every face detected, compare it with all the faces in database
                        for i in range(len(self.features_known_list)):
                            # 如果 person_X 数据不为空 / If data of person_X is not empty
                            if str(self.features_known_list[i][0]) != '0.0':
                                e_distance_tmp = self.return_euclidean_distance(
                                    self.current_frame_face_feature_list[k],
                                    self.features_known_list[i])
                                #print(f"    with person {i + 1}, the e-distance: {e_distance_tmp}")
                                self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                            else:
                                # 空数据 person_X / Empty data for person_X
                                self.current_frame_face_X_e_distance_list.append(999999999)

                        # d. 寻找出最小的欧式距离匹配 / Find the one with minimum e distance
                        similar_person_num = self.current_frame_face_X_e_distance_list.index(
                            min(self.current_frame_face_X_e_distance_list))

                        if min(self.current_frame_face_X_e_distance_list) < 0.4:
                            # 在这里更改显示的人名 / Modify name if needed
                            # self.show_chinese_name()
                            self.current_frame_name_list[k] = self.face_name_known_list[similar_person_num]
                            #print(f"    recognition result for face {k + 1}: {self.face_name_known_list[similar_person_num]}")
                            self.current_name_char=self.face_name_known_list[similar_person_num]
                        else:
                            print(f"    recognition result for face {k + 1}: unkown")

                    if "unknown" in self.current_frame_name_list:
                        self.reclassify_interval_cnt += 1

                # 4.2.1 人脸数从 1->0 / Face cnt 1->0
                elif self.current_frame_face_cnt == 0:
                    #print("  scene 2.2 人脸消失, 当前帧中没有人脸 / No face in this frame!!!")
                    self.reclassify_interval_cnt = 0
                    self.current_frame_name_list = []
                    self.current_frame_face_feature_list = []
        # cv2.imshow("camera", self.current_frame)
        img_Image = Image.fromarray(self.current_frame)
        img_PhotoImage = ImageTk.PhotoImage(image=img_Image)
        self.label.img_tk = img_PhotoImage
        self.label.configure(image=img_PhotoImage)
        # Refresh frame
        self.update_name(self.current_name_char)
        self.win.after(10, self.process)
    def update_name(self,name):
        self.label_current_name_char['text']=name
        if self.last_name!=name and name!="" and name !="unkown":
            self.last_name=name
            print("name_modified:",self.last_name)
            self.GUI_info(name)
    def Button_work(self,name):
        if name:
            add_attendance_info(name,"work")
    def Button_off_work(self,name):
        if name:
            add_attendance_info(name,"work_off")
    def GUI_info(self,name):
        tk.Label(self.frame_right_info,
                 text="智能打卡系统",
                 font=self.font_title).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)

        self.label_current_name.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_current_name_char.grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        tk.Button(self.frame_right_info,
                  text="出勤打卡",
                  command=lambda: self.Button_work(name)).grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=2,
                                                               pady=20)

        tk.Button(self.frame_right_info,
                  text='收工打卡',
                  command=lambda: self.Button_off_work(name)).grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=2,
                                                                   pady=20)

        # Show log in GUI
        self.log_all.grid(row=11, column=0, columnspan=20, sticky=tk.W, padx=5, pady=20)
        self.frame_right_info.pack()
    def run(self):
        if self.get_face_database():
            self.GUI_info(None)
            self.process()
            self.win.mainloop()
def main():
    connect_db()
    Punch_card_con = Punch_card()
    Punch_card_con.run()
if __name__ == '__main__':
    main()