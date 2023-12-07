<?xml version="1.0" encoding="utf-8"?>

<!-- ======================================================== -->
<!-- File    : PROTEUS_stakeholder.xsl                        -->
<!-- Content : PROTEUS XSLT for subjects at US - stakeholder  -->
<!-- Author  : José María Delgado Sánchez                     -->
<!-- Date    : 2023/06/07                                     -->
<!-- Version : 1.0                                            -->
<!-- ======================================================== -->

<!-- ======================================================== -->
<!-- exclude-result-prefixes="proteus" must be set in all     -->
<!-- files to avoid xmlsn:proteus="." to appear in HTML tags. -->
<!-- ======================================================== -->

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:proteus="http://proteus.us.es"
    exclude-result-prefixes="proteus"
>

    <!-- ============================================= -->
    <!-- proteus:stakeholder template                  -->
    <!-- ============================================= -->

    <xsl:template match="object[@classes='stakeholder']">
        <table class="stakeholder remus_table" id="{@id}">

            <!-- Header -->
            <xsl:call-template name="generate_header">
                <xsl:with-param name="label"   select="$proteus:lang_stakeholder"/>
                <xsl:with-param name="class"   select="'stakeholder'"/>
            </xsl:call-template>

            <!-- Role -->
            <xsl:call-template name="generate_simple_row">
                <xsl:with-param name="label"     select="$proteus:lang_role"/>
                <xsl:with-param name="content"   select="properties/stringProperty[@name='role']"/>
                <xsl:with-param name="mandatory" select="'true'"/>
            </xsl:call-template>

            <!-- Category -->
            <!-- <xsl:if test="properties/enumProperty[@name='category'] != 'nd'">
                <xsl:call-template name="generate_simple_row">
                    <xsl:with-param name="label"   select="$proteus:lang_category"/>
                    <xsl:with-param name="content" select="properties/enumProperty[@name='category']"/>
                    <xsl:with-param name="span"    select="$span"/>
                </xsl:call-template>
            </xsl:if> -->

            <!-- Comments -->
            <xsl:call-template name="generate_markdown_row">
                <xsl:with-param name="label"   select="$proteus:lang_comments"/>
                <xsl:with-param name="content" select="properties/markdownProperty[@name='comments']"/>
            </xsl:call-template>

        </table>
    </xsl:template>

</xsl:stylesheet>
