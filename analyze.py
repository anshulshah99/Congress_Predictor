def analyze():
    # Connect to the congress database and construct the following objects:
    # votes: a list of vote ids (from the id column of votes table) for votes
    #        of interest.
    # persons: a list of person ids for legislators (from the person_id column
    #          of the person_votes table) who ever casted any vote of interest.
    # X: a matrix (numpy.array) where each row corresponds to a person in
    #    persons above and each column corresponds to a vote in votes
    #    above; X[i,j] = 1 if the the vote cast by persons[i] for
    #    votes[j] is positive, or 0 otherwise.
    # y: a vector (numpy.array) where each component corresponds to a person
    #    in persons above; y[i] = 1 if the person is Republican, or 0 otherwise.

    conn = psycopg2.connect("dbname=congress")
    cur = conn.cursor()
    
    cur.execute('''
SELECT id
FROM votes
WHERE chamber = 'h' AND session = 2015
ORDER BY id;
''')

    votes = [ vote_id.strip() for vote_id, in cur ]
    vote2index = { vote_id.strip() : i for i, vote_id in enumerate(votes) }

   
    cur_persons = conn.cursor()
    cur_persons.execute('''
SELECT p.person_id, r.party, v.id, p.vote
FROM person_votes p, votes v, person_roles r
WHERE p.vote_id = v.id AND p.person_id = r.person_id AND v.chamber = 'h' AND v.session = 2015
ORDER BY p.person_id;
''')
    persons = []
    person_votes = {}
    person_party = {}
    for (person_id, party, vid, vote) in cur_persons:
        pid = str(person_id.strip())
        vid = vid.strip()
        if pid not in persons:
            persons.append(pid)
        if pid not in person_party:
            person_party[pid] = party
        if pid not in person_votes:
            person_votes[pid] = []
        if vote == "Yea" or vote == "Aye":
            person_votes[pid].append(vid)
    
    y = [1 if person_party[pid] == "Republican" else 0 for pid in persons]
   
    
            
    person2index = { person_id.strip() : i for i, person_id in enumerate(persons) }
    y = numpy.array(y)
    
    X = numpy.zeros((len(persons), len(votes)), dtype=int)
    
    
    for p in persons:
        for v in votes:
            if v in person_votes[p]:
                X[person2index[p], vote2index[v]] = 1
                
    
    cur.close()
    cur_persons.close()
    conn.close()
