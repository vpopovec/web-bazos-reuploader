# Bazos Reuploader
#### Video Demo:  https://www.youtube.com/watch?v=qhrTkPIi2-M
#### Url: https://bazos-reuploader.onrender.com/
###### Initial load may take a while (hosting scales down when inactive)
Bazos reuploader is a tool for reuploading your advertisements on bazos.sk site. It helps you gain an edge over the competition and save money on promoting your ad. Reupload all your ads with a few clicks.
* **Reupload ads**
* **Lightweight** and **fast**, only requests

## Why Use Bazos Reupload

* Save significant amount of time when reuploading ads
* Open-source, free forever

## How It Works

1. Using client's email and phone number, reuploader creates a session
2. Client enters SMS key, reuploader then downloads and deletes all their ads
3. Reuploader uploads all downloaded ads to bazos

## Implementation details
Results of uploading ads are stored in a SQLite DB. However, I opted for files to store downloaded ads, the reason is that I still need to implement a way to either match ads or fix picture reuploading process, because after 5-6 reuploads pictures get pixelated.
### Session
I use requests session to preserve cookies after a request. In addition to that I store the session cookies in a binary file so that next time the client uses this app, they don't have to authorize anymore. 
### Ad password
I have noticed that bazos platform doesn't really care about the ad password (even though they demand it for upload/delete/modify operations). All authorization is handled via "bkod" ("bcode" in english) cookie, which is granted after autorizing session via SMS code. 

## Project design
I designed the frontend in flask and backend is running purely python with synchronous and asynchronous requests with SQLite DB storing user and results information.

## Motivation
We decided to move out from a rented house, but we had bought all the furniture to furnish the house, including appliances! With dozens of pieces of furniture which we needed to sell, I decided to program a tool for reuploading all the adverts on an advertising platform, because after a few days our furniture gut pushed into the far back in search. Thanks to this tool our ads gained exposure and we were able to sell almost everything.
