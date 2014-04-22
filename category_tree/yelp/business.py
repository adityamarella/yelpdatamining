from recordtype import recordtype

Business = recordtype('Business', [
                                   'business_id',
                                   'name',
                                   'type',
                                   'open',
                                   'full_address',
                                   'city',
                                   'state',
                                   'latitude',
                                   'longitude',
                                   'neighborhoods',
                                   'hours',
                                   'stars',
                                   'review_count',
                                   'categories',
                                   'attributes',
                                   ],
                      default=None)
