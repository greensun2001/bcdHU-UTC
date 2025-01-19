import hmac
import streamlit as st
import page_contents.pg000 as pg000
import page_contents.pg001 as pg001
import page_contents.pg002 as pg002
import page_contents.pg003 as pg003
from model.r_ai_n import *
from page_contents.input_components import (
    sidebar_param_setting2conc,
    sidebar_m_mcft_params,
)


def feature00():
    """des"""
    conc = sidebar_param_setting2conc("sidebar_params_feature00")

    ls_funcs = [
        "Transferring stresses for [w]",
        "Transferring stresses for [$p_v$]",
        "Maximum shear stress for [$a_g$]",
        "Comparison (2P, m_2P, MCFT)",
    ]
    with st.sidebar:
        st.header("Choose a function", divider="green")
        func = st.radio(
            "Choose a function", ls_funcs, index=0, label_visibility="collapsed"
        )
    st.subheader(func)

    if func == ls_funcs[0]:
        pg000.pg000_f00(conc)
    elif func == ls_funcs[1]:
        pg000.pg000_f01(conc)
    elif func == ls_funcs[2]:
        pg000.pg000_f02(conc)
    elif func == ls_funcs[3]:
        pg000.pg000_f03(conc)


def feature01():
    """des"""
    with st.expander(":green[**Simplified equations**] :blue[(m_MCFT)]", expanded=True):
        eq_image = "images/m_eqs_s.png"
        st.image(eq_image, use_column_width=False)
    conc = sidebar_param_setting2conc("sidebar_params_feature01")
    st.subheader("Regression Analysis")
    s = """
    Regression analysis is based on :blue[**scipy.optimize.curve_fit**], which uses :red[non-linear least squares] to fit a defined function to data.
    """
    st.write(s)

    ls_funcs = [
        "Typical Analysis",
        "Finding parameter C",
        "Finding parameter A",
        "MC test calculation",
    ]
    ntimes, nsets = pg001.pg001_mc_init()
    with st.sidebar:
        st.header("Select regression for", divider="green")
        func = st.radio(
            "Select regression for", ls_funcs, index=0, label_visibility="collapsed"
        )
    if func == ls_funcs[0]:
        pg001.pg001_typical_ana(conc, ntimes=ntimes, nsets=nsets)
    elif func == ls_funcs[1]:
        pg001.pg001_findC(conc=conc, ntimes=ntimes, nsets=nsets)
    elif func == ls_funcs[2]:
        pg001.pg001_findA(conc=conc, ntimes=ntimes, nsets=nsets)
    elif func == ls_funcs[3]:
        pg001.pg001_MC(conc=conc, ntimes=ntimes, nsets=nsets)


def feature02():
    """des"""
    with st.expander(":green[**Simplified equations**]", expanded=False):
        eq_image = "images/m_eqs_s.png"
        st.image(eq_image, use_column_width=False)

    pg002.pg002_f00()


def feature03():
    """des"""
    st.write("")
    pg003.pg003_f00()


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        col1, col2 = st.columns(2)
        with col1:
            logo_image = "images/hu_utc.png"
            st.image(logo_image, use_column_width=False)
        with col2:
            st.write("# :rainbow[Shear program]")
        st.write("")
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

# SIDEBAR
# . LOGO
logo_image = "images/hu_utc.png"
logo_icon = "images/utc_s.png"
st.logo(image=logo_image, icon_image=logo_icon, size="large")

# . COMPONENTS
# .. FEATURES
# st.sidebar.write("## :rainbow[Select a feature]")
st.sidebar.markdown(
    "<h1 style='text-align: center; color: darkblue;'>Select a feature</h1>",
    unsafe_allow_html=True,
)
ls_choices = [
    "Updated Two-phase Model",
    "Shear transfer Regression",
    "Shear Prediction",
    "About the research",
]


feature_choice = st.sidebar.selectbox(
    "Choose Feature",
    ls_choices,
    placeholder="Click to select",
    label_visibility="collapsed",
    index=0,
)
if feature_choice == None:
    feature_choice = ls_choices[-1]

st.header(f":rainbow[{feature_choice}]", divider="rainbow")

# Main content according to page
if feature_choice == ls_choices[0]:
    feature00()

elif feature_choice == ls_choices[1]:
    feature01()

elif feature_choice == ls_choices[2]:
    feature02()

elif feature_choice == ls_choices[3]:
    feature03()
