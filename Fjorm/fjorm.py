
def generate_html( intent, prefix="" ):
    def render( k, T ):
        if T=="string":
            return "<label>{k}</label><input type='text' name='{k}' value=''/>".format(k=k)
        elif "|" in T:
            return "<label>{k}</label>\n".format(k=k).join( 
                ("<input type='radio' name='{k}' value='{v}'/>".format(k=k,v=v) % (k,v))
                for v in T.split("|")
            )
        elif "&" in T:
            return "<label>{k}</label>\n".format(k=k).join( 
                ("<input type='checkbox' name='%s' value='%s'/>" % (k,v))
                for v in T.split("&")
            )
        else:
            raise ValueError("Unknown form type: "+repr(T))
    return "\n".join(
        "<fieldset>"+render(k,T)+"</fieldset>" for (k,T) in intent.items()
    )

def parse_response( d ):
    pass
