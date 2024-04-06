import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import torch
import time
import pickle
from plot.utils import select_top_words, select_phi_from_topics, filter_phi_from_words, plot_unguide_topics, plot_seed_topics

# the phenotype topics we want to find, and the corresponding phecodes
topic_list = ['asthma', 'chf', 'copd', 'diabetes', 'epilepsy', 'hiv', 'hypertension', 'ihd', 'schizophrenia']
phecode_list = [495, 428, 496, 250, 345, 71, 401, 411, 295.1]
max_words = 3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
exp_n = torch.load("../parameters/exp_n_pres_0.pt", map_location=device)
exp_n = exp_n.cpu().detach().numpy()
V, K = exp_n.shape
beta = 0.05
phi_r = (beta + exp_n) / (beta*V + exp_n.sum(axis=1, keepdims=1))
phi_r = phi_r / phi_r.sum(axis=0, keepdims=1) # normalization over V for each topic

# read index mapping of vocab and phecode
vocab_ids = pickle.load(open("../mapping/pres_vocab_ids.pkl", "rb")) # key is icd, value is the mapped index
inv_vocab_ids = {v: k for k, v in vocab_ids.items()}
phecode_ids = pickle.load(open("../mapping/phecode_ids.pkl", "rb")) # key is phecode, value is the mapped index
tokenized_phecode_icd = pickle.load(open("../mapping/tokenized_phecode_icd.pkl", 'rb')) # get seed word-topic mapping, V x K matrix

# select phi from the chosen topics
select_phi_r, phecode_seed_dict = select_phi_from_topics(phi_r, V, phecode_list, phecode_ids, tokenized_phecode_icd)
top_words = select_top_words(select_phi_r, max_words, len(topic_list))
filter_phi_r = filter_phi_from_words(select_phi_r, phecode_list, top_words, max_words)
# top_med_name_list = [inv_vocab_ids[v].split('-')[0] for v in top_words] # show only drug name
# print(top_med_name_list)
top_med_name_list = [inv_vocab_ids[v] for v in top_words] # show complete name

# find atc meaning
# atc_mapping_df = pd.read_csv('../data/atc_ukbb_no_remove.csv')
# atc_name_dict = dict(zip(atc_mapping_df['Drug name'], atc_mapping_df['Medication ATC code']))
# top_word_names = [atc_name_dict[v] for v in top_words_list]

def extract_drug_name(drug_string):
    """Extracts the first term (drug name) from drug strings with hyphens"""
    return drug_string.split('-')[0]
update_med_name_list = [extract_drug_name(drug) for drug in top_med_name_list]
plot_unguide_topics(filter_phi_r, update_med_name_list, phecode_list, topic_list)

# seed_ind_list = [1]*27
# plot_seed_topics(filter_phi_r, top_med_name_list, phecode_list, topic_list, seed_ind_list)
