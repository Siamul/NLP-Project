# NLP-Project


## We have the pairwise sentences from a part of the Shrek plot and the Gutenberg Poetry corpus found by closest distance between the keywords of each sentence using GloVe (https://nlp.stanford.edu/projects/glove/) vectors trained with Common Crawl (840B tokens, 2.2M vocab, cased, 300d vectors) and sentence embeddings from BERT transformers (https://arxiv.org/abs/1908.10084). 

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

# Here's an example of sentence matching using BERT vectors. 

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

## I also take pairs of sentences from the plot and find the closest rhyming pair from the Gutenberg Poetry corpus using GloVe and BERT vectors. 

# Here's the example output for rhyming pairs aligned using GloVe:

-----------------------------------------------
Shrek, a green ogre who loves the solitude in his swamp, finds his life interrupted when countless fairytale characters are exiled there by order of the fairytale-hating Lord Farquaad of Duloc.
Shrek tells them that he will go ask Farquaad to send them back.

are closest to:

### Where crystal streams by flowery margents flow

### And I must tell thee, ere I go,.

-----------------------------------------------
He brings along a talking Donkey, who is the only fairytale creature who knows the way to Duloc.
Meanwhile, Farquaad tortures the Gingerbread Man into giving the location of the remaining fairytale creatures until his guards rush in with something he has been searching for: the Magic Mirror.

are closest to:

### The big high church steeple

### for the house has fallen into the hands of wicked people..

-----------------------------------------------
He asks The Mirror if his kingdom is the fairest of them all but is told that he is not even a king.
To be a king he must marry a princess and is given three options, from which he chooses Princess Fiona, who is locked in a castle tower guarded by lava and a dragon.

are closest to:

### We find one reference to his birthplace in the form of a bad pun

### The Princess of that castle was the one,.

-----------------------------------------------
The Mirror tries to mention "the little thing that happens at night" but is unsuccessful.
Shrek and Donkey arrive at Farquaad's palace in Duloc, where they end up in a tournament.

are closest to:

### Sing and Ill ease thy shoulders of thy load

### At once up to the palace in fair array they rode;.

-----------------------------------------------
The winner gets the "privilege" of rescuing Fiona so that Farquaad may marry her.
Shrek and Donkey easily defeat the other knights in wrestling-match fashion, and Farquaad accepts his offer to move the fairytale creatures from his swamp if Shrek rescues Fiona.

are closest to:

### foreigner was probably brought to Rome as a child

### From the knight's grasp. The way is dark and wild;.

-----------------------------------------------
Shrek and Donkey travel to the castle and split up to find Fiona.
Donkey encounters the dragon and sweet-talks the beast before learning that it is female.

are closest to:

### In the interior of the Wasp and Wagon

### He makes them bear before him his dragon,.

-----------------------------------------------
Dragon takes a liking to him and carries him to her chambers.
Shrek finds Fiona, who is appalled at his lack of romanticism.

are closest to:

### So to the chamber of his guest the hero goes his way,.

### incongruous adaptation of an old Homeric simile we meet with a

-----------------------------------------------
As they leave, Shrek saves Donkey, caught in Dragon's tender clutches, and forces her to chase them out of the castle.
At first, Fiona is thrilled to be rescued but is quickly disappointed when Shrek reveals he is an ogre.

are closest to:

### The names of five or six comic dramatists are known who fill

### And at first you startled me.  But I knew you still,.

-----------------------------------------------
As the three journey to Duloc, Fiona urges the two to camp out for the night while she sleeps in a cave.

are closest to:

### "We will away to the cave of Night,.

-----------------------------------------------
-----------------------------------------------

# Here's an example of the results using BERT vectors:

-----------------------------------------------

Shrek, a green ogre who loves the solitude in his swamp, finds his life interrupted when countless fairytale characters are exiled there by order of the fairytale-hating Lord Farquaad of Duloc.
Shrek tells them that he will go ask Farquaad to send them back.

are aligned to:

### And smote my brother Otter that his heart's life fled away,.

### incongruous adaptation of an old Homeric simile we meet with a

-----------------------------------------------
He brings along a talking Donkey, who is the only fairytale creature who knows the way to Duloc.
Meanwhile, Farquaad tortures the Gingerbread Man into giving the location of the remaining fairytale creatures until his guards rush in with something he has been searching for: the Magic Mirror.

are aligned to:

### Then let the sacred tribunes wait my leisure

### Can bring him to his sweet up-locked treasure,.

-----------------------------------------------
He asks The Mirror if his kingdom is the fairest of them all but is told that he is not even a king.
To be a king he must marry a princess and is given three options, from which he chooses Princess Fiona, who is locked in a castle tower guarded by lava and a dragon.

are aligned to
### He smiled and threw an acorn at a lizard

### The bride, thrice beautiful; the groom, a wizard;.

-----------------------------------------------
The Mirror tries to mention "the little thing that happens at night" but is unsuccessful.
Shrek and Donkey arrive at Farquaad's palace in Duloc, where they end up in a tournament.

are aligned to:

### Her eye might flash on his, but found it dim;.

### The grace of trees and the bloom of flowers were prized by him

-----------------------------------------------
The winner gets the "privilege" of rescuing Fiona so that Farquaad may marry her.
Shrek and Donkey easily defeat the other knights in wrestling-match fashion, and Farquaad accepts his offer to move the fairytale creatures from his swamp if Shrek rescues Fiona.

are aligned to:

### But the girl whom he saved is our hero's fair bride,.

### Illuc sis vide

-----------------------------------------------
Shrek and Donkey travel to the castle and split up to find Fiona.
Donkey encounters the dragon and sweet-talks the beast before learning that it is female.

are aligned to:

### Ner kick, ner run away, cavort,.

### Of a depending gaping servile court

-----------------------------------------------
Dragon takes a liking to him and carries him to her chambers.
Shrek finds Fiona, who is appalled at his lack of romanticism.

are aligned to:

### So keen to fold me to his heart, that I.

### Aere renidescit tellus supterque virum vi

-----------------------------------------------
As they leave, Shrek saves Donkey, caught in Dragon's tender clutches, and forces her to chase them out of the castle.
At first, Fiona is thrilled to be rescued but is quickly disappointed when Shrek reveals he is an ogre.

are aligned to:

### To drive the dolphins from the wreathed door..

### familiar to the Greek idyl of the recurring chime of the same or

-----------------------------------------------



