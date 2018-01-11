# FBGroupUserAnalysis
Given a Facebook Group ID, this program collects data on each user that has posted, commented, or liked anything in the group using Facebook's Graph API. Although Facebook has built-in group analytics, there is no information on each user and how they interact in the group. Typically, specific user identity and information is not relevant to most admins, but I was an instructor for a programming course, and this code was originally written to view which students were most active in a private group for our course so that the instructional team could give them credit.

This program is intended for smaller groups and assumes that there are less than 200 posts in the group.

This program will cache Facebook requests, and write two other files: a JSON file containing data on every user, and a txt file containing a report naming the top contributors of the Facebook group. 

To use the program, you must know the Facebook group ID of the group you want to analyze. You must be an administrator of the group if it is a closed group. Otherwise, the group must be an open group so that there are sufficient privileges for the API to work. You must also get an access token, which you can get here: https://developers.facebook.com/tools/explorer. user_managed_groups should be checked. Once you have the access token and group ID, you can replace the variables at the top of the program with the token and ID as strings.
