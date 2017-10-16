#Heplers.py
#This file is for helper functions that could be useful in multiple views/models/forms, etc

from base.models import CommitteeMember, Tally

#Note: these methods could have their performance improved if we could query the members
#  of a specified committee and do these filter operations db side
#  should there be a committee model?

def get_moderator_for_committee_members(members):
    for member in members:
        secondary_role = member.secondary_role.lower()
        if 'vice' not in secondary_role and 'moderator' in secondary_role:
            return member
    return None

    
def get_vice_moderator_for_committee_members(members):
    for member in members:
        secondary_role = member.secondary_role.lower()
        if 'vice' in secondary_role and 'moderator' in secondary_role:
            return member
    return None

def get_committee_members_with_role(members, roleAbbreviation):
    returnList = []
    for member in members:
        identities = member.identities_indicator()
        if len(identities) >= 3:
            if (identities[2] == roleAbbreviation):
                returnList.append(member)
    return returnList

def get_committee_members_with_role_from_tally(tallys, roleAbbreviation):
    m_set = set()
    for tally in tallys:
        if (tally.member.secondary_role):
            pass
        else:
            identities = tally.member.identities_indicator()
            if len(identities) >= 3:
                if (identities[2] == roleAbbreviation):
                    m_set.add(tally.pk)

    return Tally.objects.filter(pk__in=m_set)

def get_sorted_tallys(tallys):
    m_set = set()
    for tally in tallys:
        if (tally.member.secondary_role):
            pass
        else:
            m_set.add(tally.pk)

    return Tally.objects.filter(pk__in=m_set).order_by('member__display_name','member__presbytery')

def get_moderator_from_tally(tallys):
    m_set = set()
    for tally in tallys:
        if(tally.member.secondary_role):
            secondary_role = tally.member.secondary_role.lower()
            if 'vice' not in secondary_role and 'moderator' in secondary_role:
                m_set.add(tally.pk)

    return Tally.objects.filter(pk__in=m_set)

def get_vice_moderator_from_tally(tallys):
    m_set = set()
    for tally in tallys:
        if(tally.member.secondary_role):
            secondary_role = tally.member.secondary_role.lower()
            if 'vice' in secondary_role and 'moderator' in secondary_role:
                m_set.add(tally.pk)

    return Tally.objects.filter(pk__in=m_set)
