<?xml version="1.0"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

  <!--  <xsl:template match="text()"/> -->

  <xsl:template match="/">
    <html>
      <xsl:apply-templates/>
      <hr/>
      <xsl:text>Done with </xsl:text>
      <a>
        <xsl:attribute name="href">grammar2thtml.xsl</xsl:attribute>
        <xsl:text>grammar2thtml.xsl</xsl:text>
      </a>
    </html>
  </xsl:template>

  <xsl:template match="grammar">
    <h1>Grammar of <xsl:value-of select="@language"/></h1>
    <xsl:if test="@comment"><xsl:value-of select="@comment"/><br/></xsl:if>
    <xsl:if test="@src">
      <xsl:text>Source: </xsl:text>
      <a><xsl:attribute name="href"><xsl:value-of select="@src"/></xsl:attribute><xsl:value-of select="@src"/></a><br/>
    </xsl:if>
    <xsl:if test="@date">Date: <b><xsl:value-of select="@date"/></b><br/></xsl:if>
    <xsl:if test="@version">Version: <b><xsl:value-of select="@version"/></b><br/></xsl:if>
    <xsl:text>Initial term: </xsl:text>
    <a>
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="@initial"/>
      </xsl:attribute>
      <b><xsl:value-of select="@initial"/></b>
    </a>
    <xsl:choose>
      <xsl:when test="child::part">
        <h3>
          <xsl:text>Contents</xsl:text>
        </h3>
        <ol>
          <xsl:for-each select="child::part">
            <li>
              <a>
                <xsl:attribute name="href">
                  <xsl:text>#PART-</xsl:text>
                  <xsl:value-of select="@name"/>
                </xsl:attribute>
                <xsl:value-of select="@name"/>
              </a>
            </li>
          </xsl:for-each>
          <xsl:if test="descendant::description">
            <li>
              <a href="#PART-description">Description</a>
            </li>
          </xsl:if>
          <li>
            <a href="#PART-non-terminals">Non-terminals</a>
          </li>
          <li>
            <a href="#PART-terminals">Terminals</a>
          </li>
        </ol>
      </xsl:when>
      <xsl:otherwise>
        <a href="#PART-non-terminals">Non-terminals</a>,
        <a href="#PART-terminals">Terminals</a>
      </xsl:otherwise>
    </xsl:choose>
    <hr/>
    <xsl:apply-templates/>
    <hr/>
    <xsl:for-each select="descendant::non-terminal">
      <xsl:variable name="nt" select="@name"/>
      <xsl:if test="count(/descendant::rule[@name=$nt]) = 0">
        <xsl:if test="count(/descendant::system-term[@term=$nt]) = 0">
          <a>
            <xsl:attribute name="href">#<xsl:value-of select="ancestor::rule/@name"/></xsl:attribute>
            <xsl:value-of select="@name"/>.
          </a>
        </xsl:if>
      </xsl:if>
    </xsl:for-each>
    <hr/>
    <a>
      <xsl:attribute name="name">PART-non-terminals</xsl:attribute>
      <b>Usage of non-terminals and system-terms</b><xsl:text>:</xsl:text>
    </a>
    <ol>
      <xsl:for-each select="descendant::rule | descendant::system-term">
        <xsl:sort select="@name|@term"/>
        <li>
          <a>
            <xsl:attribute name="href">#<xsl:value-of select="@name|@term"/></xsl:attribute>
            <xsl:attribute name="name">USE-<xsl:value-of select="@name|@term"/></xsl:attribute>
            <i><xsl:value-of select="@name|@term"/></i>
          </a>
          <xsl:variable name="ntname" select="@name|@term"/>
          <xsl:text> in </xsl:text>
          <xsl:for-each select="/descendant::non-terminal[@name=$ntname]">
            <a>
              <xsl:attribute name="href">#<xsl:value-of select="$ntname"/><xsl:value-of select="position()"/></xsl:attribute>
              <i>
                <xsl:value-of select="ancestor::rule/@name"/>
              </i>
              <xsl:if test="position() != last()">
                <xsl:text>, </xsl:text>
              </xsl:if>
            </a>        
          </xsl:for-each>
          <xsl:if test="position() != last()">
            <xsl:text>,</xsl:text>
          </xsl:if>
          <xsl:text>
          </xsl:text>
        </li>
      </xsl:for-each>
    </ol>
    <hr/>
    <hr/>
    <a>
      <xsl:attribute name="name">PART-terminals</xsl:attribute>
      <b>Usage of terminals</b><xsl:text>:</xsl:text>
    </a>
    <ol>
      <xsl:for-each select="descendant::terminal">
        <xsl:sort select="@symbol"/>
        <xsl:variable name="tsymb" select="@symbol"/>
        <xsl:if test="count(following::terminal[@symbol=$tsymb])=0">
          <li>
            <xsl:text disable-output-escaping="yes">"</xsl:text>
            <b>
              <xsl:value-of select="@symbol"/>
            </b>
            <xsl:text disable-output-escaping="yes">" in </xsl:text>
            <xsl:for-each select="/descendant::terminal[@symbol=$tsymb]">
              <a>
                <xsl:attribute name="href">#<xsl:value-of select="ancestor::rule/@name"/></xsl:attribute>
                <i>
                  <xsl:value-of select="ancestor::rule/@name"/>
                </i>
                <xsl:if test="position() != last()">
                  <xsl:text>, </xsl:text>
                </xsl:if>
              </a>        
            </xsl:for-each>
            <xsl:if test="position() != last()">
              <xsl:text>,</xsl:text>
            </xsl:if>
            <xsl:text>
            </xsl:text>
          </li>
        </xsl:if>
      </xsl:for-each>
    </ol>
    <hr/>
    <address>
      <a><xsl:attribute name="href">http://math.uwb.edu.pl/~bancerek/</xsl:attribute>Grzegorz Bancerek</a>,
      <a><xsl:attribute name="href">mailto:bancerek@mizar.org</xsl:attribute>bancerek@mizar.org</a>
    </address>
  </xsl:template>

  <xsl:template match="part">
    <h2>
      <a>
        <xsl:attribute name="name">
          <xsl:text>PART-</xsl:text>
          <xsl:value-of select="@name"/>
        </xsl:attribute>
        <xsl:value-of select="@name"/>
      </a>
    </h2>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="system-terms">
    <br/>
    <b>System terms</b> (<a href="#PART-non-terminals">usage</a>):<br/>
    <xsl:apply-templates>
      <xsl:sort select="@term"/>
    </xsl:apply-templates>
    <hr/>
  </xsl:template>

  <xsl:template match="system-term">
    <a>
      <xsl:attribute name="name"><xsl:value-of select="@term"/></xsl:attribute>
      <i>
        <xsl:value-of select="@term"/>
      </i>
    </a>
    <xsl:if test="position() != last()">
      <xsl:text>,
      </xsl:text>
    </xsl:if>
    <xsl:if test="position() = last()">
      <xsl:text>.
      </xsl:text>
    </xsl:if>
  </xsl:template>
    
  <xsl:template match="grammar/rule">
    <a>
      <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
    </a>
    <br></br>
    <table border="0" cellspacing="0" cellpadding="2" width="680" bgcolor="#E7EAF1">
      <tr>
        <td colspan="2">
          <i><xsl:value-of select="@name"/></i>
          <xsl:text> =</xsl:text>
        </td>
        <td>
          <a>
            <xsl:attribute name="href">#USE-<xsl:value-of select="@name"/></xsl:attribute>
            <xsl:text>use</xsl:text>
          </a>
        </td>
      </tr>
      <tr>
        <td rowspan="1" width="25">
          <xsl:text></xsl:text>
        </td>
        <td width="615">
          <xsl:apply-templates/>
          <xsl:text> .</xsl:text>
        </td>
      </tr>
    </table>
    <xsl:variable name="rname" select="@name"/>
    <xsl:if test="/grammar/description/descitem[@subject=$rname]">
      <a>
        <xsl:attribute name="href">#DESC-<xsl:value-of select="@name"/></xsl:attribute>
        <xsl:text>, description</xsl:text>
      </a>
    </xsl:if>
    <xsl:if test="position()!=last()">
      <br></br>
    </xsl:if>
  </xsl:template>

  <xsl:template match="page">
    <table border="0" cellspacing="0" cellpadding="2" width="680" bgcolor="#E7EAF1">
      <xsl:apply-templates/>
    </table>
    <br></br>
    <br></br>
  </xsl:template>

  <xsl:template match="part/rule">
    <a>
      <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
    </a>
    <br></br>
    <table border="0" cellspacing="0" cellpadding="2" width="680" bgcolor="#E7EAF1">
      <tr>
        <td colspan="2">
          <i><xsl:value-of select="@name"/></i>
          <xsl:text> =</xsl:text>
        </td>
        <td>
          <a>
            <xsl:attribute name="href">#USE-<xsl:value-of select="@name"/></xsl:attribute>
            <xsl:text>use</xsl:text>
          </a>
        </td>
      </tr>
      <tr>
        <td rowspan="1" width="25">
          <xsl:text></xsl:text>
        </td>
        <td width="615">
          <xsl:apply-templates/>
          <xsl:text> .</xsl:text>
        </td>
      </tr>
    </table>
    <xsl:variable name="rname" select="@name"/>
    <xsl:if test="/grammar/description/descitem[@subject=$rname]">
      <a>
        <xsl:attribute name="href">#DESC-<xsl:value-of select="@name"/></xsl:attribute>
        <xsl:text>, description</xsl:text>
      </a>
    </xsl:if>
    <xsl:if test="position()!=last()">
      <br></br>
    </xsl:if>
  </xsl:template>

  <xsl:template match="page/rule">
    <tr>
      <td colspan="3">
        <a>
          <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
        </a>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <i><xsl:value-of select="@name"/></i>
        <xsl:text> =</xsl:text>
      </td>
      <td>
        <a>
          <xsl:attribute name="href">#USE-<xsl:value-of select="@name"/></xsl:attribute>
          <xsl:text>use</xsl:text>
        </a>
      </td>
    </tr>
    <tr>
      <td rowspan="1" width="25">
        <xsl:text></xsl:text>
      </td>
      <td width="615">
        <xsl:apply-templates/>
        <xsl:text> .</xsl:text>
      </td>
    </tr>
    <xsl:variable name="rname" select="@name"/>
    <xsl:if test="/grammar/description/descitem[@subject=$rname]">
      <a>
        <xsl:attribute name="href">#DESC-<xsl:value-of select="@name"/></xsl:attribute>
        <xsl:text>, description</xsl:text>
      </a>
    </xsl:if>
    <xsl:if test="position()!=last()">
      <tr></tr>
    </xsl:if>
  </xsl:template>

  <xsl:template match="non-terminal">
    <xsl:variable name="ntname" select="@name"/>
    <xsl:text> </xsl:text>
    <a>
      <xsl:attribute name="href">#<xsl:value-of select="@name"/></xsl:attribute>
      <xsl:attribute name="name"><xsl:value-of select="@name"/><xsl:value-of select="count(preceding::non-terminal[@name=$ntname])+1"/></xsl:attribute>
      <i><xsl:value-of select="./@name"/></i>
    </a>
  </xsl:template>

  <xsl:template match="terminal">
    <xsl:text disable-output-escaping="yes"> "</xsl:text>
    <b><xsl:value-of select="./@symbol"/></b>
    <xsl:text disable-output-escaping="yes">" </xsl:text>
  </xsl:template>

  <xsl:template match="subrule[@kind='zero-or-one']">
    <xsl:text> [</xsl:text>
    <xsl:apply-templates/>
    <xsl:text> ]</xsl:text>
  </xsl:template>

  <xsl:template match="subrule[@kind='zero-or-more']">
    <xsl:choose>
      <xsl:when test="descendant::separator">
        <xsl:text> [</xsl:text>
        <xsl:apply-templates select="subrule | terminal | non-terminal"/>
        <xsl:text> {</xsl:text>
        <xsl:apply-templates select="separator"/>
        <xsl:apply-templates select="subrule | terminal | non-terminal"/>
        <xsl:text> } ]</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text> {</xsl:text>
        <xsl:apply-templates/>
        <xsl:text> }</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="subrule[@kind='one-or-more']">
    <xsl:apply-templates select="subrule | terminal | non-terminal"/>
    <xsl:text> {</xsl:text>
    <xsl:apply-templates select="separator"/>
    <xsl:apply-templates select="subrule | terminal | non-terminal"/>
    <xsl:text> }</xsl:text>
  </xsl:template>

  <xsl:template match="subrule[@kind='alternative']">
    <xsl:if test="count(parent::rule/child::*)!=1">
      <xsl:text> (</xsl:text>
    </xsl:if>
    <xsl:for-each select="child::*[position()!=last()]">
      <xsl:apply-templates select="self::*"/>
      <xsl:text> |</xsl:text>
      <!--br-->
    </xsl:for-each>
    <xsl:apply-templates select="child::*[position()=last()]"/>
    <xsl:if test="count(parent::rule/child::*)!=1">
      <xsl:text> )</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="description">
    <h2>
      <a name="PART-description">Description</a>
    </h2>
    <xsl:apply-templates>
      <xsl:sort select="subject"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="descitem">
    <p>
      <b>
        <i>
          <a>
            <xsl:attribute name="href">#<xsl:value-of select="@subject"/></xsl:attribute>
            <xsl:attribute name="name">DESC-<xsl:value-of select="@subject"/></xsl:attribute>
            <xsl:value-of select="@subject"/>
          </a>
        </i>
      </b>
      <br>
      </br>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="ref">
    <a>
      <xsl:attribute name="href">#<xsl:value-of select="@target"/></xsl:attribute>
      <xsl:value-of select="@target"/>
    </a>
  </xsl:template>
</xsl:stylesheet>
