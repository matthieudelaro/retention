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

