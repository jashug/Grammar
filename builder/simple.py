def getQuestion(feed, triage, time):
    try:
        q = triage.recommend(time).next()
    except StopIteration:
        q = feed.next()
        while q in triage:
            q = feed.next()
    return feed[q]
