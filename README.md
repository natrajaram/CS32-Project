# Diversity-Aware Feed Builder

## Overview
This project builds a personalized content feed that balances relevance and diversity. Given a set of user interests and a collection of “pins” (text descriptions), the system selects a subset of content that is both highly relevant to the user and not overly repetitive.

This models a key challenge in modern content platforms: how to show users what they like without showing too much of the same thing.

---

## Motivation
Platforms that recommend content often face a tradeoff:
- Show the most relevant items → results become repetitive
- Show diverse items → results may feel less personalized

This project explores how to computationally balance these competing goals using a simple algorithm.

---

## Problem Statement
Given:
- A list of user interests
- A dataset of pins (text descriptions)

Design an algorithm that:
1. Scores each pin based on relevance to the user
2. Selects a fixed number of pins
3. Ensures diversity by penalizing similar content

---

## Features
- Personalized feed generation based on user input
- Relevance scoring using keyword matching
- Diversity-aware selection using similarity penalties
- Adjustable diversity level (low, medium, high)
- Clear explanation of why each pin was selected

---

## How It Works

### Step 1: Input
The user provides:
- Interests (e.g., tennis, fitness, food)
- Desired feed size
- Diversity preference

### Step 2: Relevance Scoring
Each pin is scored based on how many words match the user’s interests.

### Step 3: Similarity Check
Pins are compared using word overlap. If a candidate pin is too similar to already selected pins, it is penalized.

### Step 4: Feed Construction
The algorithm iteratively selects the best-scoring pin while accounting for diversity.

---

## Example

### User Input
- Interests: tennis, fitness, food
- Feed size: 4
- Diversity: medium

### Dataset
- tennis drills for beginners
- cool outfit ideas
- pilates core routine
- healthy smoothie recipes
- fun travel plans
- gym strength workout
- best tourist destinations

### Output
--- Your Personalized Feed ---
- tennis drills for beginners
- healthy smoothie recipes
- pilates core routine
- gym strength workout

--- Explanation ---
Pins were selected to match your interests while avoiding repetitive content.

---

### Credits
This project is inspired by real-world recommendation systems used in platforms like Pinterest and other content discovery applications.

