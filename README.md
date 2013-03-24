DOM Prophet 
=============  

What is this? We'll let this very real dictionary entry describe it:   
> DOM Prophet | dəmˈpräfit |  
> noun  
> 1. a utility regarded as an inspired teacher or proclaimer of the will of the DOM  

But, in all seriousness; this is a tool we built at a 24 hour hackathon to bring transparency
to what sort of actions (and by extension, events) users perform on your website.
By using a graph datastore (neo4j), we're able to mirror the DOM of a page on your site in all permutations, without
any content. If your DOM structure is at all semantic, this can be useful to you.

To query this information, we chose to use normal CSS selectors. CSS is low friction enough for a designer/product manager
to understand it. The next time they come to you and asks: "how many people clicked on this button in this particular box",
you can either set up google analytics, or point them to this utility.
