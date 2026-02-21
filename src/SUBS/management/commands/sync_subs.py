from typing import Any
from django.core.management.base import BaseCommand
from SUBS.models import Subscription

class Command(BaseCommand):#basic hello world function
    
    def handle(self, *args: Any, **options: Any):
        mysubs=Subscription.objects.filter(isactive=True)
        for sub in mysubs:
            sub_perms=sub.permissions.all()
            for group in sub.groups.all():
                for perm in sub.permissions.all():
                    group.permissions.set(sub_perms)
        print('Homie ,you trippin,gay ass motherfuc**er')


        

# Find students enrolled in both courses
math_students = {"Alice", "Bob", "Charlie", "David"}
physics_students = {"Charlie", "David", "Eve", "Frank"}

both_courses = math_students & physics_students
print(f"Taking both: {both_courses}")  # {'Charlie', 'David'}

only_math = math_students - physics_students
print(f"Only math: {only_math}")  # {'Alice', 'Bob'}

# Real-world: Find common followers
user1_followers = {"alice", "bob", "charlie"}
user2_followers = {"bob", "david", "charlie"}

mutual_followers = user1_followers & user2_followers
print(mutual_followers)  # {'bob', 'charlie'}        