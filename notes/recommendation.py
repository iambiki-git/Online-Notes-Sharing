# import pandas as pd
# from django.contrib.auth.models import User
# from .models import Note, NoteDownload

# def recommend_notes(user):
#     # Get all downloads
#     downloads = NoteDownload.objects.select_related('note').all()

#     # Create a DataFrame
#     df = pd.DataFrame(list(downloads.values('user_id', 'note_id')))

#     # Pivot the DataFrame to create a user-item matrix
#     user_item_matrix = df.pivot_table(index='user_id', columns='note_id', aggfunc='size', fill_value=0)

#     # Use collaborative filtering (e.g., cosine similarity) or any other recommendation logic here
#     from sklearn.metrics.pairwise import cosine_similarity

#     # Calculate the cosine similarity between users
#     similarity_matrix = cosine_similarity(user_item_matrix)

#     # Create a Series for the specific user
#     user_index = user_item_matrix.index.get_loc(user.id)
#     user_similarities = similarity_matrix[user_index]

#     # Get similar users
#     similar_users_indices = user_similarities.argsort()[-2:-7:-1]  # Top 5 similar users

#     # Get recommended notes based on these users
#     recommended_notes = set()
#     for similar_user_index in similar_users_indices:
#         similar_user_id = user_item_matrix.index[similar_user_index]
#         recommended_notes.update(user_item_matrix.columns[user_item_matrix.loc[similar_user_id] > 0])

#     return Note.objects.filter(id__in=recommended_notes)

import pandas as pd
from django.contrib.auth.models import User
from .models import Note, NoteDownload
from sklearn.metrics.pairwise import cosine_similarity

def recommend_notes(user):
    # Get all downloads
    downloads = NoteDownload.objects.select_related('note').all()

    # Create a DataFrame
    df = pd.DataFrame(list(downloads.values('user_id', 'note_id')))

    # Check if the DataFrame is empty
    if df.empty:
        # print("No downloads found for user.")
        return Note.objects.none()  # Return empty queryset if no downloads

    # Pivot the DataFrame to create a user-item matrix
    user_item_matrix = df.pivot_table(index='user_id', columns='note_id', aggfunc='size', fill_value=0)

    # Calculate the cosine similarity between users
    similarity_matrix = cosine_similarity(user_item_matrix)

    # Create a Series for the specific user
    user_index = user_item_matrix.index.get_loc(user.id)
    user_similarities = similarity_matrix[user_index]

    
    similar_users_indices = user_similarities.argsort()[-2:][::-1]  # Top 2 similar users


      # Check if we have found similar users
    if not similar_users_indices.any():
        # print(f"No similar users found for user: {user.username}")
        return Note.objects.none()  # Return empty queryset if no similar users

    # Get indices of the top 5 similar users
    similar_users_indices = user_similarities.argsort()[-6:-1][::-1]  # Top 5 similar users

    # Get recommended notes based on these users
    recommended_notes = set()
    for similar_user_index in similar_users_indices:
        similar_user_id = user_item_matrix.index[similar_user_index]
        # Add notes downloaded by similar users that the current user has not downloaded
        recommended_notes.update(user_item_matrix.columns[user_item_matrix.loc[similar_user_id] > 0])

   # Fetch recommended notes from the database
    recommended_notes_queryset = Note.objects.filter(id__in=recommended_notes)
    # print(f"Recommended notes for user {user.username}: {recommended_notes_queryset.values_list('title', flat=True)}")

    return recommended_notes_queryset

