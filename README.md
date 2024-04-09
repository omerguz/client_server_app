# MillionDolarTrivia

## Introduction

Welcome to our trivia game, a client-server application that implements a trivia contest. Players who can be either bot or human, receive random true or false facts about the English Premier Leage clubs Tottenham, Manchester United, Manchester City, Liverpool, Chelsea, and Arsenal.
Each player must answer the question correctly within 10 seconds, otherwise he is out of the game.  

## Flow of the Game

1. Each player activates the client and wait for new server offers to connect.
2. When the server offer a client to join the contest, the player enter his name or a funny name.
3. After 10 seconds, the game starts and the server is starting to ask the players to answer a trivia questions.
4. A player that answered incorrectly, eliminates from the game, unless all players answers incorrectly, another round is held in that case.
6. If a player didnt answered within 10 seconds, he disconnects immediately due to a  violation of the games rules.
7. The player that lasts alone in game wins.

## Important rules

- 1: It is higly recommended that at least 2 players can play the game
- 2: A player that doesnt respond, is kicked out of the game immediately and can join the next contest

