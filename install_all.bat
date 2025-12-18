:: ============================================
:: INSTALL ALL DEPENDENCIES FOR FIND MINUTIAE APP
:: ============================================

@echo off
echo -------------------------------------------
echo ACTIVATING ENVIRONMENT venv_fingeflow_37_fix
echo -------------------------------------------
call venv_fingeflow_37_fix\Scripts\activate

echo -------------------------------------------
echo UPGRADING PIP
echo -------------------------------------------
python -m pip install --upgrade pip

echo -------------------------------------------
echo INSTALLING CORE ML STACK
echo -------------------------------------------
pip install numpy==1.19.5
pip install gast==0.4.0
pip install h5py==3.1.0
pip install tensorflow==2.5.0
pip install tensorflow-estimator==2.5.0
pip install keras-nightly==2.5.0.dev2021032900

echo -------------------------------------------
echo INSTALLING IMAGE PROCESSING DEPENDENCIES
echo -------------------------------------------
pip install opencv-python==4.5.5.64
pip install scikit-image==0.19.3
pip install scipy==1.7.3
pip install PyWavelets==1.3.0

echo -------------------------------------------
echo INSTALLING FINGERFLOW
echo -------------------------------------------
pip install fingerflow==3.0.1

echo -------------------------------------------
echo INSTALLING GUI + UTILITIES
echo -------------------------------------------
pip install customtkinter==5.2.2
pip install pillow==9.5.0
pip install matplotlib==3.5.3
pip install python-dateutil==2.9.0.post0
pip install pandas==1.3.5
pip install pytz==2025.2

echo -------------------------------------------
echo INSTALLING REMAINING DEPENDENCIES
echo -------------------------------------------
pip install absl-py==0.15.0
pip install astunparse==1.6.3
pip install cached-property==1.5.2
pip install cachetools==5.5.2
pip install certifi==2025.10.5
pip install charset-normalizer==3.4.4
pip install cycler==0.11.0
pip install darkdetect==0.8.0
pip install flatbuffers==1.12
pip install fonttools==4.38.0
pip install google-auth==2.41.1
pip install google-auth-oauthlib==0.4.6
pip install google-pasta==0.2.0
pip install grpcio==1.34.1
pip install idna==3.10
pip install imageio==2.31.2
pip install importlib-metadata==6.7.0
pip install Keras-Applications==1.0.8
pip install Keras-Preprocessing==1.1.2
pip install kiwisolver==1.4.5
pip install Markdown==3.4.4
pip install MarkupSafe==2.1.5
pip install networkx==2.6.3
pip install oauthlib==3.2.2
pip install opt-einsum==3.3.0
pip install packaging==24.0
pip install protobuf==3.20.3
pip install pyasn1==0.5.1
pip install pyasn1-modules==0.3.0
pip install pyparsing==3.1.4
pip install requests==2.31.0
pip install requests-oauthlib==2.0.0
pip install rsa==4.9.1
pip install six==1.15.0
pip install tensorboard==2.11.2
pip install tensorboard-data-server==0.6.1
pip install tensorboard-plugin-wit==1.8.1
pip install termcolor==1.1.0
pip install tifffile==2021.11.2
pip install typing-extensions==3.7.4.3
pip install urllib3==2.0.7
pip install Werkzeug==2.2.3
pip install wrapt==1.12.1
pip install zipp==3.15.0

echo -------------------------------------------
echo INSTALLATION COMPLETED SUCCESSFULLY!
echo YOU CAN NOW BUILD THE EXE USING:
echo python -m PyInstaller build37.spec
echo -------------------------------------------

pause
