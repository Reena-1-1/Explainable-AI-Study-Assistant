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