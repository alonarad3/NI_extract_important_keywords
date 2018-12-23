# NI_extract_important_keywords

Research :
---------------------------------------------
Data:
(1) some tagging is available via techCurnch . 
(2) sources of tags / topics?
(3) can create a dataset with 	

Detection: [topic modeling]
	unsupervised with database:
		(1) TF-IDF: the idea is that if a word appears in a doc more than natural appearance
		than it might be content related/ doc related.
		(2) adjusted TF-IDF: positioning scoring / offset
		(3) LDA - latent space - clustring
		(4) topic modeling is the search keyword :)
	supervised with database:
		(1) RNN's/DNN / other of this sort - any form of supervised learning
		(2) Naive Bayes / Logistic.....
	from article:
		(1) Grammar modules (such as spacy) -  entity Recognition + N_subject and etc'
		(2) RAKE
		(3) TextRANK

------------------------------------------------
ALG Description:
-------------------------------------------------
article = scraped article.

general algorithm:
	get candidates - > work with several algorithms (implemented rake on content),NP Chunks on title
	merge Candidates - > currently mostly stemming supported
	remove Keywords -> use predictors/any other technique to remove and approve keywords
		[scoring mechanism -> not implemented [the idea is to use several techniques to combine one score]]
	return set of Keywords
  
----------------------------------
ISSUES / TO IMPROVE:
----------------------------------
		GENERAL STEPS:
		1. Annotated Data-Set:
			allows to evulate results, the given techCrunch tags where not exactly the
			requirement as i understood it, could serve as modifications/ machine_learning for the predictors
		2. Creating A DB:
			a. tags DB -> with relations
			b. articles DB - commit articles to DB (https://techcrunch.com/sitemap-index-1.xml)
			c. use / explore public data-sets
		ALG IMPROVEMENTS
		recall:
		1. General Topics / Deduced Topics:
			can only extract words that appear in the article!
			example : movie aquaman talks about entrainment / Funding when raising Money
			a. by supervised learning
			b. by unsupervised topic modeling (such as LDA) 
			c. by tags relations [example Target - > e-commerce]
			d. could also serve as arg for predictors
			e. from wiki categories
		2. Add Extraction Algs:
			a) simple Title Extraction Rule / Patterns [such as raises-> funding, gift guide:, "-" or capitlization in title
			e.g Twitter's newest feature is reigniting the 'iPhone vs Android' war - > iPhone | Android 
			b) unsupervised modeling (*)as described before
			c) supervised learning
			c) entity recognition/ NP_CHUNKS in article_content.
		3. Add COMPANIES/Personal Data - Bases
			e.g "Slack says it will comply with sanctions and block Iran-based activity, apologizes for botched first effort"- slack
		4. create Scorer for Title's extraction:
			e.g "Slack says it will comply with sanctions and block Iran-based activity, apologizes for botched first effort"- slack -> disapproved
			e.g "The top smartphone trends to watch in 2019" -> top smartphone trends -> disapproved
			(a) based on positioning of extracted text
			(b) root dependency
			(c) root sentence rule
		5.preProcessing Args:
			note: should be done carefully
			a)local Bigram / Trigram Detector e.g [ men in black movie]
			b)global Bigram / Trigram Detector e.g [united states]
			c)stemming might be helpful [but needed a dict to convert back in implementation, 
			and going back rules]
		precision:
		1. Improve deduplication of Keywords 
			a) identify when can deduplicate (e.g [u'gofundme campaign', u'runaway GoFundMe campaign', u'gofundme','campaign']) by splitting keywords into buckets.
		2. implement scorer and dynamic bars (espically for rake - by content length etc')  
		3. Identify and deal with few concepts articles:
			e.g : 
		4. check wikepdia distance from original [sometimes the returned page is not what intented]
		5. improve General Words alg. 
		e.g keywords such as ["back","long"]
		6. dealing with multiple subjects articles [such as The top smartphone trends to watch in 2019]
-------------------------------------------------	
ALG IN DEPTH:	
-------------------------------------------------
get Candidates algorithms description:
(?) concat commonPhrases
get candidates from title:
	(?) identify pattern (example - gift guide: ) 
	parse Title -> creates a POS,DEP,ENTITY_RECOGINTION dicts
	by np chunks + entity recognition:
		[addChunk by dep, 
		approveAndModifyCandidate]
	by entity recognition:
		[add entity by type,
		removeCandidates by entity type]
	Returns candidates,localPredictors 
	
get	candidates from description by rake:
	(?) preprocess for rake 
	get candidates from Rake
	clean candidates [approveAndModifyChunk?]
	get relevant localPredictors():
		pos_tagging
		in_title
	keep only values above score of 1.0

		
approveAndModifyChunk	
cleanChunk
leaveOnlyNounsAndAdj
removeSmartStopListWords (such as it, they , etc'...)
			
			
returns candidates + algorithm predictors


Merge Candidates:
	by stemming equivalance
	(?) by contain - not implemented

remove keywords:
	first removal of candidates that do not hold for certain patterns [such as 50 million and etc']
	(# note that this will also remove #101 dalmaties)
	remove general tech words - e.g: company, techcrunch, etc'
	approve high confidence form algorithm
	approve by wiki (up t0 4 calls)

returns candidates 
