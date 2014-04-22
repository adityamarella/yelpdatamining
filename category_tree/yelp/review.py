from recordtype import recordtype

Review = recordtype('Review', [
                               'review_id',
                               'business_id',
                               'user_id',
                               'date',
                               'type',
                               'text',
                               'stars',
                               'votes',
                               ],
                    default=None)
