# Trivia King👑

## Introduction

Welcome to Trivia King👑, an alternative evaluation for reservists, designed for the Intro to Nets 2023/4 project. Trivia King👑 is a client-server application that implements a trivia contest. Players receive random true or false facts and must answer correctly as quickly as possible.

## Version

Version 1.0

## Example Run

Let's walk through a typical example run of Trivia King👑:

1. Team Mystic starts their server, which begins broadcasting offer announcements.
2. Players Alice, Bob, and Charlie start their clients and connect to the server.
3. After all players have connected, the game begins with a trivia question.
4. Players receive questions from the server and respond with their answers.
5. The server evaluates answers, declares winners, and proceeds to the next question or ends the game.
6. After the game concludes, a summary message is sent to all players.

## Suggested Architecture

- **Client**: Single-threaded application with three states: looking for a server, connecting to a server, and game mode.
- **Bot**: Implemented for teams of 3, behaves similarly to the client but randomly chooses answers.
- **Server**: Multi-threaded application managing multiple clients, with states for waiting and game mode.

## Packet Formats

- UDP Announcements: Includes a magic cookie, message type, server name, and server port.
- TCP Data: Predefined team name sent by client followed by communication between client and server.

## Tips and Guidelines

- Choose creative player names, hard-code them for quick startup.
- Use ChatGPT or Github Copilot for assistance.
- Implement error handling for invalid inputs and network issues.
- Utilize ANSI color for fun output.
- Collect and print interesting statistics after the game finishes.

## Code Quality Expectations

### Static Quality
- Proper layout, meaningful function and variable names.
- Comments and documentation for functions and major code blocks.
- Avoid hard-coded constants, especially IP addresses or ports.

### Dynamic Quality
- Check return values of functions.
- Handle exceptions properly.
- Avoid busy-waiting.
- Isolate network code to a single network.

## Source Control

- Host code in a GitHub repository.
- Ensure commits are made by all team members.
- Use proper commit messages and branches.

## How to Submit

Please submit the link to your GitHub repository (not private) on Moodle. Make sure to commit regularly, with only the last commit before the deadline considered.

Good luck with your Trivia King👑 project!
