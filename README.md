# Retention

## Example
The following GIF show what happens when backups are generated every few hours, and the algorithm is ran to evict them every few hours, over a period of ~4 months.

With a policy of 7 daily, 4 weekly, 12 monthly, 10 yearly backups, the retention algorithm marks the following backups as:
![retention.gif](retention.gif)
- Green: days whose backups have been evicted
- Purple: backups to be evicted
- Blue: yearly backups
- Darker Blue: monthly backups
- Red: weekly backups
- Orange: daily backups

## Details
Retention is designed with backups in mind: out of a given list of backups, which ones should be retained
in order to comply with a given Policy?
The other backups should be evicted to free-up disk space.

For example:
	There is one backup every 1 day during the last past 2 years.
	The Policy requires 4 weekly backups and 12 monthly backups.
	So there is two windowType: weekly and monthly.
  
### Let's start with weekly backups:
#### The policy expects 4 weekly backups, which means:
- one backup >= four weeks ago, and < five weeks ago
- one backup >= three weeks ago, and < four weeks ago
- one backup >= two weeks ago, and < three weeks ago
- one backup >= a week ago, and < two weeks ago
Since all other backups will be evicted, 12 hours later there might not be
any backup < two weeks ago. That's why a 5th backup is kept:
- one backup < a week ago,
which will take the spot of the previous backup within a week.
      
#### The policy is applied as follow:
1) select the youngest backup which is less than 4+1 weeks old.
2) select the next backup which is older
	than the previously selected backup + one week.
3) Repeat step 2 until the youngest backup is selected.
    
### Let's handle the monthly backups:
#### The policy expects 12 monthly backups, which means:
- one backup >= 12 months ago, and < 13 months ago
- ...
- one backup >= 1 month ago, and < two months ago
- one backup < a month ago
    
#### BUT: how long is a month? 31 days? 30 days? The average => 30.5 days ?
But sometimes it's only 28 days long! The choice is hard to make.
The chosen solution: the algorithm selects monthly backups
	that are no more than 28 days away from one another. It selects as many
	monthly backups as required to cover
	the period of the last (30.5 days) * (required monthly backups + 1)
#### So the policy expects 12 monthly backups, which means:
- one backup >= 368.5 (=396.5 - 28) days ago, and < 396.5 (=(12+1)x30.5) days ago
- one backup >= 368.5 - 28, and < 368.5 days ago
- ...
- one backup >= ~28 days ago, and < ~56 days ago
- one backup < ~28 days ago
