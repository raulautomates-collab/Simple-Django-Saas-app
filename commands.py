# Get unique words from text
text = "the quick brown fox jumps over the lazy dog"
unique_words = set(text.split())
print(unique_words)  # {'the', 'quick', 'brown', 'fox', ...}

# Find duplicate entries
def find_duplicates(items):
    seen = set()
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return duplicates

numbers = [1, 2, 3, 2, 4, 5, 3, 6]
print(find_duplicates(numbers))  # {2, 3}

text="Is this the real life,Is is a fantasy,opwn a landslide,no escape from reality"

def dupes(items):
    confirmed=set()
    duplicates=set()

    for item in items:
        if item in confirmed:
            duplicates.add(item)
        else:
            confirmed.add(item)    
    return duplicates        

numbers=[1,1,3,4,8,9,9,2,5]
print(dupes(numbers))

# Check if user has required permissions
def user_can_access(user_permissions, required_permissions):
    return required_permissions.issubset(user_permissions)

user_perms = {"read", "write", "delete"}
required = {"read", "write"}

if user_can_access(user_perms, required):
    print("Access granted")

# Get unique tags from multiple posts
post1_tags = {"python", "django", "web"}
post2_tags = {"python", "flask", "api"}
post3_tags = {"django", "rest", "api"}

all_tags = post1_tags | post2_tags | post3_tags
print(all_tags)  # All unique tags