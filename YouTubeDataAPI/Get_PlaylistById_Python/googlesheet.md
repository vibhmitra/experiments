## Generating Playlist URLs in Google Sheets
This formula will generate YouTube video URLs.
After cleaning up and removing the duplicates, you can use the following formula to generate a YouTube playlist:

For example, if your YouTube URLs are in column A, you can use the following formula in any row other than A itself to generate the playlist urls.

```googlesheets
=LET(
  raw_ids, ARRAYFORMULA(REGEXEXTRACT(A1:A, "(?:v=|/)([\w-]{11})(?:[^\w-]|$)")),
  ids, UNIQUE(TOCOL(raw_ids, 3)),
  video_matrix, WRAPROWS(ids, 50, ""),
  
  BYROW(video_matrix, LAMBDA(row, 
    "https://www.youtube.com/watch_videos?video_ids=" & 
    TEXTJOIN(",", TRUE, row)
  ))
)
```

## Limitations
- YouTube doesn't allow generating playlists longer than 50 videos using the URL method, so each playlist is capped at 50 videos.
