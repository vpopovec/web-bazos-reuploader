# Bazos Reuploader
### Video Demo:  https://www.youtube.com/watch?v=qhrTkPIi2-M
Bazos reuploader is a tool for reuploading your advertisements on bazos.sk site. It helps you gain an edge over the competition and save money on promoting your ad. Reupload all your ads with a few clicks.
* **Reupload ads**
* **Lightweight** and **fast**, only requests

## Why Use Bazos Reupload

* Save significant amount of time when reuploading ads
* Download all your ads (along with pictures) for future use

## How It Works

1. Using client's email and phone number, reuploader creates a session
2. Client enters SMS key, reuploader then downloads and deletes all their ads
3. Reuploader uploads all downloaded ads to bazos

## Implementation details
Instead of using a database to store information I opted for files. The reason behind that is that I have to store pictures which would probably make the database large.
### Session
I use requests session to preserve cookies after a request. In addition to that I store the session cookies in a binary file so that next time the client uses this app, they don't have to authorize anymore. 
### Ad password
I have noticed that bazos platform doesn't really care about the ad password (even though they demand it for upload/delete/modify operations). All authorization is handled via "bkod" ("bcode" in english) cookie, which is granted after autorizing session via SMS code. 

## Project design
First I was considering using PWA for this project, since I've already built a working backend for reuploading bazos ads. 
I ran into some issue, I wasn't familiar with typescript so I decided to use flask. 
I designed the frontend via flask (using finance as a template) and backend is running purely python with synchronous and asynchronous requests.

## Bugs
I *struggled* with this project. My most frustrating bug to date was mixing up "sms-code" for "sms-confirm". I got unexpected behavior, I scanned the whole code, tested it on CLI version just to find a typo. However, I did learn during that time that flask operates on threads and I need to save my requests session inside a file when redirecting.

## Motivation
We decided to move out from a rented house but we had bought all the furniture to furnish the house, including appliances! With dozens of pieces of furniture which we needed to sell, I decided to program a tool for reuploading all the adverts on an advertising platform, because after a few days our furniture gut pushed into the far back in a search. Thanks to this tool our ads gained exposure and we were able to sell almost everything.