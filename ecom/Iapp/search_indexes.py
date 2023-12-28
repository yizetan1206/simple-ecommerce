from haystack import indexes 
from .models import Products 


class ProductIndex(indexes.SearchIndex, indexes.Indexable): 
    text = indexes.EdgeNgramField(document=True, use_template=True)
    id = indexes.CharField(model_attr='id') 
    content_auto = indexes.EdgeNgramField(model_attr='name')
    description = indexes.CharField(model_attr="description") 
      
    def get_model(self):
      return Products
      
    def index_queryset(self, using=None): 
      """Used when the entire index for model is updated.""" 
      return self.get_model().objects.all()