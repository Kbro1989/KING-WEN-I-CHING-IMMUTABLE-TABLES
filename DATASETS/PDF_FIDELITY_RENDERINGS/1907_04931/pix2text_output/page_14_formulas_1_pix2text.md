rege :Dege Disribuion

C.2 ADDITIONAL DATASET DETAILS
ewewepenedi or topeantiLik- e and naon dasts.
The Flickr dataset originates from NUS-wides. The SNAP website collected Flickr data from four different sources including NUS-wide, and generated an un-directed graph. One node in the graph represents one image uploaded to Flickr. If two images share some common properties (e.g., same geographic location, same gallery, comments by the same user, etc.), there is an edge between the nodes of these two images. We use as the node features the 500-dimensional bag-of-word representation of the images provided by NUS-wide. For labels, we scan over the 81 tags of each image and manually merged them to 7 classes. Each image belongs to one of the 7 classes.

The Yelp dataset is prepared from the raw $\dot{\mathtt{j}}$ son data of businesses, users and reviews provided in tecanciles wair $| |$ . For nodes and edges, we scan the friend list of each user in the raw $\dot{\eta}$ son file of users. If two users are friends, we create an edge between them. We then filter out all the reviews by each user and separate the reviews into words. Each review word is converted to a 300-dimensional vector using the Word2Vec model pre-trained on GoogleNews**. The word vectors of each node are added and normalized to serve as the node feature (i.e., $x_{v}$ ). As for the node labels, we scan the raw json file of businesses, and use the categories of the businesses reviewed by a user $v$ as the multi-class label of $v$ .

For the Amazon dataset, a node is a product on the Amazon website and an edge $( u , v )$ is created if products $u$ and $v$ are bought by the same customer. Each product contains text reviews (converted to STANTEN5N5T5 34234 200, and use the obtained vectors as the node feature. The labels represent the product categories
ure $5$ shwse tedegre distiuion ofthe fie gah.Apin $k$ is $p$ . $( k , p )$ in the plot means the abiliy of a nod avingdegre at least

C.3 ADDITIONAL DETAILS IN EXPERIMENTAL CONFIGURATION
ab 4sumaic s L L ona tnetalinecodes.
he pime or Gantna a l baslines s Aam Kinm 0 r l baslines and datasets, we perform grid search on the hyperparameter space defined by:

Hidndnensom $\{1 2 8 , 2 5 6 , 5 1 2 \}$ 