package com.lorepo.iceditor.client.controller;

public class CalculateMaxScore {
	int pageMaxScore = 0;

	public void addMaxScore (int maxScore){
		pageMaxScore += maxScore;
	}

	public int getMaxScore () {
		return pageMaxScore;
	}

	public void clear() {
		pageMaxScore = 0;
	}
}
