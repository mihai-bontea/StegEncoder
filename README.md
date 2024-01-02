# StegEncoder

## Overview

StegEncoder is a steganography tool used for **hiding secret messages inside of images and audio files**. It uses a modified version of the LSB substitution method, in which instead of having the modified bits in consecutive bytes, every **k** bytes are left unmodified. **k**  will be the maximum number of bytes that can be skipped while also having the secret message fit inside the carrier file. 
This method has the benefit that it spreads the changes evenly throughout the image, leading to much fewer potential anomalies in one spot.

The secret message is **compressed** with the maximum compression level, in order to reduce the quality loss of the carrier file.

For further protecting the secret message, it is encrypted using **the one-time pad(OTP) technique**. This technique ensures **perfect secrecy** as long as:

* The length of the key is at least the length of the plaintext.

* The key must be random.

* The key must never be reused.

* The key must be kept secret by the communicating parties.

For true randomness, the **secrets library** is used, which provides the best sources of entropy available to the operating system, **including hardware entropy sources**.

## Encode tab

The user must select a file, and insert the secret message inside the textbox. The number of LSBs used can be changed, otherwise it will default to 1 bit. If the *"Use Encryption"* checkbox is ticked, the *"Copy key"* button can be used to copy the mask to clipboard.


![gui1](https://github.com/mihai-bontea/StegEncoder/assets/79721547/6005d82b-2282-48f3-b7f9-a37ffc9d04ed)

## Decode tab

Similarly to the encode tab, the user must select a file and the number of LSBs used. Optionally, an encryption key can be provided, if encryption has been used when encoding.


![gui3](https://github.com/mihai-bontea/StegEncoder/assets/79721547/70fb2f2d-7274-47cc-aee9-d1d9fb618d86)

## Architecture

The application is written with the Model-View-Controller design pattern in mind. The model, namely, the part of the application responsible for managing and manipulating the data is comprised of the WavType, ImageType, VideoType, FileType and OneTimePad classes.

The main functions responsible for changing/retrieving the LSBs of a byte stream are contained within FileType. Beyond that, each new file type added must only implement the means of retrieving the modifiable bytes and of writing them to a file, making it simple to add new functionality.

![image](https://github.com/mihai-bontea/StegEncoder/assets/79721547/e6d6ea62-7ee6-476e-aefc-56c81ccabcbb)
