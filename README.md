# Hubei-College-Admission-Checker

## 功能

本脚本用于湖北省普通高校招生录取查询，并在查询到录取状态后自动发送邮件通知。

## 使用方法

1. **配置邮件发送地址**
   在 `main.py` 文件中，根据注释进行邮件发送地址的配置。

2. **配置查询信息**
   在 `config.json` 文件中，填写以下信息：
   - `报名号`
   - `出生年月日`
   - `接收邮件的邮箱`

### 详细步骤

1. **克隆或下载本项目**
   ```bash
   git clone https://github.com/GooGuJiang/Hubei-College-Admission-Checker.git
   cd Hubei-College-Admission-Checker
   ```

2. **配置邮件发送信息**
   在 `main.py` 文件中，配置邮件发送服务器和发送地址。例如：


3. **填写查询信息**
   打开 `config.json` 文件，填写报名号、出生年月日和接收通知的邮箱。例如(支持多个报名号查询)：
   ```json
   {
     "accounts": [
       {
         "ksh": "your_registration_number1",
         "sfzh": "YYMMDD",
         "email": "recipient1@example.com"
       },
       {
         "ksh": "your_registration_number2",
         "sfzh": "YYMMDD",
         "email": "recipient2@example.com"
       }
     ]
   }
   ```

4. **运行脚本**
   使用以下命令运行脚本进行录取状态查询：
   ```bash
   docker-compose up -d
   ```

### 注意事项

- 确保网络连接畅通，以便脚本能够访问查询接口。
- 邮件发送信息正确无误，以保证通知邮件能够正常发送。


## 许可证

本项目采用 Apache License Version 2.0 进行开源，详细信息请查看 LICENSE 文件。