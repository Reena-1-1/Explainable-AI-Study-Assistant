Literature Survey

1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)

Summary:

- This paper introduces Retrieval-Augmented Generation (RAG), which combines information retrieval with a language generation model.
- The system retrieves relevant documents and uses their content to help generate answers.
- The approach aims to make generated responses more informative by grounding them in retrieved information.

Relation to our project:
Our Study Assistant follows a similar idea by retrieving relevant passages from an uploaded PDF and using them to support answers with page references.

2. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks (Reimers and Gurevych, 2019)

Summary:

- This paper presents Sentence-BERT, a method for producing meaningful vector representations of sentences.
- These representations allow sentences to be compared efficiently using similarity measures.
- The method supports semantic search, where results are selected by meaning rather than exact keyword matches.

Relation to our project:
Our project uses Sentence Transformers to represent text chunks as embeddings, helping retrieve passages that are semantically relevant to a student's question.

3. Billion-scale Similarity Search with GPUs (Johnson, Douze, and Jégou, 2017)

Summary:

- This paper introduces FAISS, a library designed for efficient similarity search and clustering of dense vectors.
- It explains methods for finding similar vectors among large collections of data.
- FAISS supports fast retrieval, making it useful for applications that compare questions with document representations.

Relation to our project:
Our Study Assistant uses FAISS to search for text chunks whose embeddings are similar to the user's question and retrieve relevant passages from a PDF.

4. “Why Should I Trust You?”: Explaining the Predictions of Any Classifier (Ribeiro, Singh, and Guestrin, 2016)

Summary:

- This paper introduces LIME, a technique for explaining individual machine-learning predictions.
- LIME approximates a complex model locally to show which input features influence a particular prediction.
- The method aims to help people understand and evaluate the behaviour of machine-learning systems.

Relation to our project:
LIME is relevant to the broader goal of Explainable AI because it focuses on making model decisions easier to understand. Our project uses retrieved evidence passages and page citations to help users verify answers, rather than implementing LIME itself.