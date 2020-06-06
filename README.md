## Fill_in_blank Program Problems Generator

## 基于多模型比较的程序填空题智能出题系统研究与实现

> **Model Introduction**

​			The final selected model is the Con-BI-RNN model. The structure of the model is as follows:

![](D:\课程\毕业论文\图片\模型结构图.jpg)

> **System Architecture**

​			The system architecture diagram is as follows:

![](D:\课程\毕业论文\图片\架构图.jpg)

> **Installation**

1. Packages

   ```shell
   pip install requirements.txt
   ```

2. EFP(Element Fill-in-blank Problem) Web Server

   ```shell
   python manage.py runserver 127.0.0.1:8000
   ```

3. Judge Server

   ```shell
   cd judger
   python judge_server.py
   ```

4. Judge Client 1

   ```shell
   cd judger
   python judge_client_1.py
   ```

5. Judge Client 2

   ```shell
   cd judger
   python judge_client_2.py
   ```