# NLP-Project

------------------------------------------------

# Dataset Creation through Alignment

To convert the plot of Shrek from Wikiplots into Poetry using closest distances for mean vector of keywords from Gutenberg Poetry corpus, run:

> python plot2poem_glove.py <glove_file_name>

You can use the pre-trained glove vectors as model: https://nlp.stanford.edu/projects/glove/

To convert the plot of Shrek from Wikiplots into Poetry using closest bert sentence embedding distances from Gutenberg Poetry corpus, run:

> python plot2poem_BERT.py <model_name>

You can find an overview of the models available here: https://www.sbert.net/docs/pretrained_models.html

To create the aligned dataset using GloVe vectors, run:

> python nmt_dataset_plot2poem_glove.py <glove_file_name> <no_of_processes>

To create the aligned dataset using BERT sentence embeddings, run:

> python nmt_dataset_plot2poem_bert.py <model_name> <no_of_processes>

Both codes uses multiprocessing for speedup and you have mention the number of processes as the third argument.

You can download all the datasets, the compiled embeddings files, and the annoy object here: 
https://drive.google.com/drive/folders/1FYxKooQ0dbOMZcJjkP2tfLfyhuo0bWuU?usp=sharing

To find the closest lines in the poetry dataset for our own text, put the text in input.txt and run:

> python text2poem_glove.py

for matched lines using glove and

> python text2poem_BERT.py <model_name>

for matched lines using BERT.

Examples of these matching are provided at the end.

-------------------------------------------------

# Attention-based Seq2seq model from (https://github.com/jadore801120/attention-is-all-you-need-pytorch) 

First you need to create a torchtext dataset from the files generated above. The code for this creation is given in preprocess_text2poetry.py. To use this code, you basically need two text files where the lines are aligned so that the line 'n' in file 1 translates to line 'n' in file 2. So, first preprocess the dataset by running:

> python preprocess_text2poetry.py -data_src <aligned_src_file_name> -data_trg <aligned_target_file_name> -save_data <data_file_name>

Then, start the training by running:

> python train.py -data_pkl <data_file_name> -embs_share_weight -proj_share_weight -label_smoothing -output_dir output -b <batch_size> -warmup 128000 -epoch 400 -save_mode <best/all>

You can download the trained weights here (weights will be added as the training completes):
https://drive.google.com/drive/folders/16eIUa26n-Zmz1lWgZywY5pYmgeadodwY?usp=sharing

-------------------------------------------------

# Unsupervised Neural Machine Translation from (https://github.com/artetxem/undreamt):

To start the training run:

> python train.py --src nonpoetry.txt --trg poetry.txt --src_embeddings ./glove.42B.300d.w2v.txt --trg_embeddings ./glove.42B.300d.w2v.txt --save prosaic2poetry --cuda --batch 16

The training for this is quite slow. You can download the trained weights here:
https://drive.google.com/drive/folders/1iSBNM2mV6QviJD1myLQ18dRGDPQH3j7-?usp=sharing

To translate a sentence using the trained weights, write the sentences separated by '\n' in input.txt and run:

> python translate.py prosaic2poetry.final.src2trg.pth -i input.txt -o output.txt

You will find the converted outputs in output.txt

-----------------------------------------------

# Retranslating into another language and back to remove poeticness.

I have tried translating poetic verses into german and back to remove the poeticness and therefore, obtain an aligned dataset of poetic and non-poetic verses. I utilized the pretrained models (https://opennmt.net/Models-py/) from OpenNMT-py (https://github.com/OpenNMT/OpenNMT-py). The models utilized SentencePiece tokenized text. To convert the original poetry dataset in './poetry.txt' to a SentencePiece tokenized dataset saved to './poetry_sp.txt', run:

> python sentencepiece_encode.py

Change directory to OpenNMT-py and then, to translate the poetry dataset into german run:

> python translate.py -model ./averaged-10-epoch.pt -src ./poetry_sp.txt -output ./german.txt -replace_unk -gpu 0

To translate the poetry dataset back into english run:

> python translate.py -model ./iwslt-brnn2.s131_acc_62.71_ppl_7.74_e20.pt -src ./german1.txt -output ./text1.txt -replace_unk -gpu 0

### We have the pairwise sentences from a part of the Shrek plot and the Gutenberg Poetry corpus found by closest distance between the keywords of each sentence using GloVe (https://nlp.stanford.edu/projects/glove/) vectors trained with Common Crawl (840B tokens, 2.2M vocab, cased, 300d vectors) and sentence embeddings from BERT transformers (https://arxiv.org/abs/1908.10084). 

-----------------------------------------------
# Here's an example of the sentence matching using GloVe.

-----------------------------------------------
-----------------------------------------------
Shrek, a green ogre who loves the solitude in his swamp, finds his life interrupted when countless fairytale characters are exiled there by order of the fairytale-hating Lord Farquaad of Duloc.

is closest to:

### Then the grave, that dark friend of my limitless dreams.

-----------------------------------------------
Shrek tells them that he will go ask Farquaad to send them back.

is closest to:

### And I must tell thee, ere I go,.

-----------------------------------------------
He brings along a talking Donkey, who is the only fairytale creature who knows the way to Duloc.

is closest to:

### And creatures to whom only God is kind,.

-----------------------------------------------
Meanwhile, Farquaad tortures the Gingerbread Man into giving the location of the remaining fairytale creatures until his guards rush in with something he has been searching for: the Magic Mirror.

is closest to:

### for the house has fallen into the hands of wicked people..

-----------------------------------------------
He asks The Mirror if his kingdom is the fairest of them all but is told that he is not even a king.

is closest to:

### him. So Pheidon king of the Thesprotians told me. Moreover.

-----------------------------------------------
To be a king he must marry a princess and is given three options, from which he chooses Princess Fiona, who is locked in a castle tower guarded by lava and a dragon.

is closest to:

### The Princess of that castle was the one,.

-----------------------------------------------
The Mirror tries to mention "the little thing that happens at night" but is unsuccessful.

is closest to:

### How horrible to see this thing at night!.

-----------------------------------------------
Shrek and Donkey arrive at Farquaad's palace in Duloc, where they end up in a tournament.

is closest to:

### At once up to the palace in fair array they rode;.

-----------------------------------------------
The winner gets the "privilege" of rescuing Fiona so that Farquaad may marry her.

is closest to:

### For a worthy husband deserves a girl who is wealthy,.

-----------------------------------------------
Shrek and Donkey easily defeat the other knights in wrestling-match fashion, and Farquaad accepts his offer to move the fairytale creatures from his swamp if Shrek rescues Fiona.

is closest to:

### From the knight's grasp. The way is dark and wild;.

-----------------------------------------------
Shrek and Donkey travel to the castle and split up to find Fiona.

is closest to:

### Untill they to York castle came.

-----------------------------------------------
Donkey encounters the dragon and sweet-talks the beast before learning that it is female.

is closest to:

### He makes them bear before him his dragon,.

-----------------------------------------------
Dragon takes a liking to him and carries him to her chambers.

is closest to:

### So to the chamber of his guest the hero goes his way,.

-----------------------------------------------
Shrek finds Fiona, who is appalled at his lack of romanticism.

is closest to:

### And horror, at my own careless cruelty,.

-----------------------------------------------
As they leave, Shrek saves Donkey, caught in Dragon's tender clutches, and forces her to chase them out of the castle.

is closest to:

### The Lady takes Torrent past the Lions, into the Castle..

-----------------------------------------------
At first, Fiona is thrilled to be rescued but is quickly disappointed when Shrek reveals he is an ogre.

is closest to:

### And at first you startled me.  But I knew you still,.

-----------------------------------------------
As the three journey to Duloc, Fiona urges the two to camp out for the night while she sleeps in a cave.

is closest to:

### "We will away to the cave of Night,.

#########################################################################################################################

# Here's an example of sentence matching using BERT vectors (stsb-roberta). 

#########################################################################################################################

-----------------------------------------------

Shrek, a green ogre who loves the solitude in his swamp, finds his life interrupted when countless fairytale characters are exiled there by order of the fairytale-hating Lord Farquaad of Duloc.

is closest to:

### And smote my brother Otter that his heart's life fled away,.

-----------------------------------------------

Shrek tells them that he will go ask Farquaad to send them back.

is closest to:

### "He calls his wish, it comes; he sends it back,.

-----------------------------------------------

He brings along a talking Donkey, who is the only fairytale creature who knows the way to Duloc.

is closest to:

### And the donkey is he who can't see the ..

-----------------------------------------------

Meanwhile, Farquaad tortures the Gingerbread Man into giving the location of the remaining fairytale creatures until his guards rush in with something he has been searching for: the Magic Mirror.

is closest to:

### Can bring him to his sweet up-locked treasure,.

-----------------------------------------------

He asks The Mirror if his kingdom is the fairest of them all but is told that he is not even a king.

is closest to:

### Each claim'd; not all their mighty kingdom's power,.

-----------------------------------------------

To be a king he must marry a princess and is given three options, from which he chooses Princess Fiona, who is locked in a castle tower guarded by lava and a dragon.

is closest to:

### The bride, thrice beautiful; the groom, a wizard;.

-----------------------------------------------

The Mirror tries to mention "the little thing that happens at night" but is unsuccessful.

is closest to:

### Her eye might flash on his, but found it dim;.

-----------------------------------------------

Shrek and Donkey arrive at Farquaad's palace in Duloc, where they end up in a tournament.

is closest to:

### Schrutan and stout Gibek into the tourney rode,.

-----------------------------------------------

The winner gets the "privilege" of rescuing Fiona so that Farquaad may marry her.

is closest to:

### But the girl whom he saved is our hero's fair bride,.

-----------------------------------------------
Shrek and Donkey easily defeat the other knights in wrestling-match fashion, and Farquaad accepts his offer to move the fairytale creatures from his swamp if Shrek rescues Fiona.

is closest to:

### like by Imbrius. As two lions snatch a goat from the hounds that.

-----------------------------------------------
Shrek and Donkey travel to the castle and split up to find Fiona.

is closest to:

### Ner kick, ner run away, cavort,.

-----------------------------------------------
Donkey encounters the dragon and sweet-talks the beast before learning that it is female.

is closest to:

### Only the monkey chatters, & discordant the parrot screams:.

-----------------------------------------------
Dragon takes a liking to him and carries him to her chambers.

is closest to:

### So keen to fold me to his heart, that I.

-----------------------------------------------
Shrek finds Fiona, who is appalled at his lack of romanticism.

is closest to:

### Oft finding them slatterns void of love;.

-----------------------------------------------
As they leave, Shrek saves Donkey, caught in Dragon's tender clutches, and forces her to chase them out of the castle.

is closest to:

### To drive the dolphins from the wreathed door..

-----------------------------------------------
At first, Fiona is thrilled to be rescued but is quickly disappointed when Shrek reveals he is an ogre.

is closest to:

### How the young gleaner was much frightened, and how happy he was.

-----------------------------------------------
As the three journey to Duloc, Fiona urges the two to camp out for the night while she sleeps in a cave.

is closest to:

### Steal home and cry herself to sleep..

-----------------------------------------------
-----------------------------------------------

## I also take pairs of sentences from the plot and approximate the closest rhyming pair (I take the closest poetry sentence for each plot sentence and then, take a rhyming sentence that is closest for the other plot sentence. I take the least distant pair among these two pairs) from the Gutenberg Poetry corpus using GloVe and BERT vectors. 

# Here's the example output for rhyming pairs aligned using GloVe:

-----------------------------------------------
Shrek, a green ogre who loves the solitude in his swamp, finds his life interrupted when countless fairytale characters are exiled there by order of the fairytale-hating Lord Farquaad of Duloc.
Shrek tells them that he will go ask Farquaad to send them back.

are aligned to:

### Then the grave, that dark friend of my limitless dreams.

### From Hell and shall I tell thee how he seems

-----------------------------------------------
He brings along a talking Donkey, who is the only fairytale creature who knows the way to Duloc.
Meanwhile, Farquaad tortures the Gingerbread Man into giving the location of the remaining fairytale creatures until his guards rush in with something he has been searching for: the Magic Mirror.

are aligned to:

### And creatures to whom only God is kind,.

### So have I with the magic of the mind

-----------------------------------------------
He asks The Mirror if his kingdom is the fairest of them all but is told that he is not even a king.
To be a king he must marry a princess and is given three options, from which he chooses Princess Fiona, who is locked in a castle tower guarded by lava and a dragon.

are aligned to:

### He is the king of peace when all is done

### The Princess of that castle was the one,.

-----------------------------------------------
The Mirror tries to mention "the little thing that happens at night" but is unsuccessful.
Shrek and Donkey arrive at Farquaad's palace in Duloc, where they end up in a tournament.

are aligned to:

### How horrible to see this thing at night!.

### So going at the last he came in sight

-----------------------------------------------
The winner gets the "privilege" of rescuing Fiona so that Farquaad may marry her.
Shrek and Donkey easily defeat the other knights in wrestling-match fashion, and Farquaad accepts his offer to move the fairytale creatures from his swamp if Shrek rescues Fiona.

are aligned to:

### Why then my maiden Aunt is big with child

### From the knight's grasp. The way is dark and wild;.

-----------------------------------------------
Shrek and Donkey travel to the castle and split up to find Fiona.
Donkey encounters the dragon and sweet-talks the beast before learning that it is female.

are aligned to:

### Untill they to York castle came.

### As a dog the raging beast became

-----------------------------------------------
Dragon takes a liking to him and carries him to her chambers.
Shrek finds Fiona, who is appalled at his lack of romanticism.

are aligned to:

### So to the chamber of his guest the hero goes his way,.

### Of sense bereft how long I cannot say

-----------------------------------------------
As they leave, Shrek saves Donkey, caught in Dragon's tender clutches, and forces her to chase them out of the castle.
At first, Fiona is thrilled to be rescued but is quickly disappointed when Shrek reveals he is an ogre.

are aligned to:

### For when behind the Fairy hill

### And at first you startled me.  But I knew you still,.

-----------------------------------------------
As the three journey to Duloc, Fiona urges the two to camp out for the night while she sleeps in a cave.
Shrek and Donkey stargaze while Shrek tells stories about great ogres and says that he will build a wall around his swamp when he returns.

are aligned to:

### "We will away to the cave of Night,.

### Then tell me more about your good fool knight

-----------------------------------------------

# Here's an example of the results using BERT vectors:

-----------------------------------------------


-----------------------------------------------
Shrek, a green ogre who loves the solitude in his swamp, finds his life interrupted when countless fairytale characters are exiled there by order of the fairytale-hating Lord Farquaad of Duloc.
Shrek tells them that he will go ask Farquaad to send them back.

are aligned to:

### And smote my brother Otter that his heart's life fled away,.

### Go then return’d the sire without delay

-----------------------------------------------

He brings along a talking Donkey, who is the only fairytale creature who knows the way to Duloc.
Meanwhile, Farquaad tortures the Gingerbread Man into giving the location of the remaining fairytale creatures until his guards rush in with something he has been searching for: the Magic Mirror.

are aligned to:

### and Danaans according to his own pleasure

### Can bring him to his sweet up-locked treasure,.

-----------------------------------------------

He asks The Mirror if his kingdom is the fairest of them all but is told that he is not even a king.
To be a king he must marry a princess and is given three options, from which he chooses Princess Fiona, who is locked in a castle tower guaon.

are aligned to:

### Each claim'd; not all their mighty kingdom's power,.

### Which God likes best into thir inmost bower

-----------------------------------------------

The Mirror tries to mention "the little thing that happens at night" but is unsuccessful.
Shrek and Donkey arrive at Farquaad's palace in Duloc, where they end up in a tournament.

are aligned to:

### Dont link yourself with vulgar folks whove got no fixd abode

### Schrutan and stout Gibek into the tourney rode,.

-----------------------------------------------

The winner gets the "privilege" of rescuing Fiona so that Farquaad may marry her.
Shrek and Donkey easily defeat the other knights in wrestling-match fashion, and Farquaad accepts his offer to move the fairytale creatures from his swamp if Shrek rescues Fiona.

are aligned to:

### But the girl whom he saved is our hero's fair bride,.

### And steal from earth its demons where they glide

-----------------------------------------------

Shrek and Donkey travel to the castle and split up to find Fiona.
Donkey encounters the dragon and sweet-talks the beast before learning that it is female.

are aligned to:

### Ner kick, ner run away, cavort,.

### The dolphin wheels the sea cows snort

-----------------------------------------------

Dragon takes a liking to him and carries him to her chambers.
Shrek finds Fiona, who is appalled at his lack of romanticism.

are aligned to:

### Come my beloved let us to bed and take our pleasure of

### Oft finding them slatterns void of love;.

-----------------------------------------------

As they leave, Shrek saves Donkey, caught in Dragon's tender clutches, and forces her to chase them out of the castle.
At first, Fiona is thrilled to be rescued but is quickly disappointed when Shrek reveals he is an ogre.

are aligned to:

### To drive the dolphins from the wreathed door..

### Such deep remorse for Rudeger in their inmost hearts they bore

-----------------------------------------------

As the three journey to Duloc, Fiona urges the two to camp out for the night while she sleeps in a cave.
Shrek and Donkey stargaze while Shrek tells stories about great ogres and says that he will build a wall around his swamp when he returns.

are aligned to:

### they had laid them the nurse went back into the house to go to

### Sez de bull frog, "D-runk!" sez de ole owl, "Whoo!".

-----------------------------------------------




