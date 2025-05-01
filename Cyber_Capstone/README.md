Infante Antivirus

Infante Antivirus is a behavior-based malware detection system leveraging machine learning to identify malicious software. It features a user-friendly GUI for scanning files and integrates with AWS EC2 for scalable cloud-based scanning.
    
Project Overview

    Machine Learning Model: Utilizes a Random Forest Classifier trained on EMBER dataset features.

    GUI Application: Built with Tkinter, This allows users to select and scan CSV files.

    Cloud Integration: Deploys scanning capabilities on an AWS EC2 instance, accessible via API Gateway.

Features

    Behavior-Based Detection: Analyzes file features like histograms, byte entropy, and strings.

    User-Friendly Interface: Simple GUI for selecting files and viewing scan results.

    Cloud Scalability: Offloads scanning to AWS EC2, enabling scalable and efficient processing.

    Result Logging: Outputs predictions to predictions_output.csv for record-keeping.

Installation

    Clone the Repository:

git clone https://github.com/AidanInfante/Cyber-Capstone.git
cd Cyber-Capstone

Run all python scripts within /finalized/setup to create needed output files and have folder organization structure found below

Create a Virtual Environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:

    pip install -r requirements.txt

    Place the Model File: Ensure Infante_Antivirus_Model.joblib is in the project root directory.

Usage

    Run the Application:

    python full_script_gui.py

    Scan a File:

        Click "Browse Cleaned CSV" to select a CSV file.

        Click "Start Scanning" to initiate the scan.

        View results in the GUI and check predictions_output.csv for detailed output.

AWS EC2 Deployment

    Launch an EC2 Instance:

        Use Amazon Linux.

        Configure security groups to allow necessary ports.

    Deploy the Backend:

        SSH into the EC2 instance.

        Clone the repository and set up the environment as above.

    Set Up API Gateway:

        Create a new API in AWS API Gateway.

        Configure routes to forward requests to your EC2 instance.

Project Structure

Cyber_Capstone/

├── Diagrams/

        Sequence-Diagram.md    # Displays project structure
        Sequence-Diagram.png    # Downloadable image of structure

├── drafts/

        scan_and_quarintine.py     # Previous iteration of final script
        scan.py    #Previous iteration of final script

├── ember/ 

        _init_.cpyhton-310.pyc     # ember file imported, but unused
        _init_.py     # ember file imported, but unused
        features.cpython-310.pyc     # ember file imported, but unused

├── finalized/ 

        quarintine/    # empty folder for future quarintine implementation
        setup-files/    # files used to create final scripts

            ember-dataset/     # data imported for training and demo
                ember_dataset_2018_2.tar    # file to extract from ember README (too large to upload to github)
                features.py    # script of different file features
                README.md     # ember README giving instructions to import data, but only used to import data (other instructions there, but stayed unused as I built my own scripts for my project)  
                test_features.jsonl    # tests dataset to compare to Random Forest Model accuracy, need to extract from ember README (too large to upload to github)
                train_features_0.jsonl     # data to analyze and use to train, need to extract from ember README (too large to upload to github)
                train_features_1.jsonl     # data to analyze and use to train, need to extract from ember README (too large to upload to github)
                train_features_2.jsonl     # data to analyze and use to train, need to extract from ember README (too large to upload to github)
                train_features_3.jsonl     # data to analyze and use to train, need to extract from ember README (too large to upload to github)
                train_features_4.jsonl     # data to analyze and use to train, need to extract from ember README (too large to upload to github)
                train_features_5.jsonl     # data to analyze and use to train, need to extract from ember README (too large to upload to github)

            create_clean_features.py    # script that flattens nested JSON for model training
            ember_features.csv     # initial nested JSON flattening script output, needs to be created by generate_csv.py as it is too large to upload to github
            generate_csv.py     # created the initial ember_features.csv
            train_model.py     # uses the cleaned features to train and save the Random Forest Classifier
            predict.py    # creates the predictions of what the antivirus model should get
        cleaned_features.csv    # output of the clean flattening script, needs to be created by create_clean_features.py as it is too large to upload to github
        Demo.mp4    # demo video for presentation
        full_script_gui.py  # final and full script that runs antivirus and scans csv files
        Infante_Antivirus_Model.joblib     # trained Random Forest Classifier used for final script, must be created by train_model.py as it is too large to upload to github
        predictions_output.csv     # output of the predictions script
        requirements.txt    # detailed text with the different imports needed for the scripts to run
├── README.md     # this file detailing the project
        

Acknowledgments

    EMBER Dataset by Endgame Inc.
    H. Anderson and P. Roth

    AWS for cloud infrastructure.

    OpenAI for assistance.
